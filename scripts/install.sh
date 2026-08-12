#!/usr/bin/env sh
set -eu

repository="${PEPPER_CARROT_REPOSITORY:-KanadeK/pepper-carrot-codex-pet}"
ref="${PEPPER_CARROT_REF:-main}"
source_root="${PEPPER_CARROT_SOURCE_ROOT:-}"
pet_id="pepper-carrot"
codex_root="${CODEX_HOME:-${HOME}/.codex}"
pets_root="${codex_root}/pets"
target="${pets_root}/${pet_id}"
backup_root="${codex_root}/pet-backups"
stage_root=""
backup_path=""
installed="false"

restore_on_failure() {
  status=$?
  trap - EXIT INT TERM
  if [ "${status}" -ne 0 ] &&
     [ "${installed}" = "false" ] &&
     [ -n "${backup_path}" ] &&
     [ ! -e "${target}" ] &&
     [ -e "${backup_path}" ]; then
    mv "${backup_path}" "${target}"
  fi
  if [ -n "${stage_root}" ] && [ -d "${stage_root}" ]; then
    rm -rf "${stage_root}"
  fi
  exit "${status}"
}
trap restore_on_failure EXIT INT TERM

sha256_for() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{ print $1 }'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{ print $1 }'
  else
    echo "No SHA-256 tool found. Install sha256sum or shasum." >&2
    return 1
  fi
}

assert_checksum() {
  file_path="$1"
  relative_path="$2"
  checksum_file="$3"
  expected="$(awk -v path="${relative_path}" '$2 == path { print $1; exit }' "${checksum_file}")"
  if [ -z "${expected}" ]; then
    echo "Missing checksum for ${relative_path}" >&2
    return 1
  fi
  actual="$(sha256_for "${file_path}")"
  if [ "${actual}" != "${expected}" ]; then
    echo "Checksum mismatch for ${relative_path}" >&2
    return 1
  fi
}

if [ -L "${pets_root}" ]; then
  echo "Refusing to operate through a symlinked pets directory: ${pets_root}" >&2
  exit 1
fi
mkdir -p "${pets_root}"
if [ -L "${target}" ]; then
  echo "Refusing to replace a symlinked pet directory: ${target}" >&2
  exit 1
fi

stage_root="$(mktemp -d "${pets_root}/.pepper-carrot.stage.XXXXXX")"
stage_pet="${stage_root}/pet"
stage_checksums="${stage_root}/checksums.txt"
mkdir -p "${stage_pet}"

if [ -n "${source_root}" ]; then
  cp "${source_root}/checksums.txt" "${stage_checksums}"
  for name in pet.json spritesheet.webp provenance.json; do
    cp "${source_root}/pet/${name}" "${stage_pet}/${name}"
  done
else
  raw_root="https://raw.githubusercontent.com/${repository}/${ref}"
  curl -fsSL "${raw_root}/checksums.txt" -o "${stage_checksums}"
  for name in pet.json spritesheet.webp provenance.json; do
    curl -fsSL "${raw_root}/pet/${name}" -o "${stage_pet}/${name}"
  done
fi

for name in pet.json spritesheet.webp provenance.json; do
  assert_checksum "${stage_pet}/${name}" "pet/${name}" "${stage_checksums}"
done

if [ -e "${target}" ]; then
  mkdir -p "${backup_root}"
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  token="$(od -An -N4 -tx1 /dev/urandom 2>/dev/null | tr -d ' \n' || printf '%s' "$$")"
  backup_path="${backup_root}/${pet_id}-install-${timestamp}-${token}"
  mv "${target}" "${backup_path}"
fi

mv "${stage_pet}" "${target}"
installed="true"

echo "Installed Pepper | Pepper&Carrot to ${target}"
if [ -n "${backup_path}" ]; then
  echo "Previous pet backup: ${backup_path}"
fi
echo "Open Settings > Pets, choose Refresh, then select Pepper | Pepper&Carrot."
