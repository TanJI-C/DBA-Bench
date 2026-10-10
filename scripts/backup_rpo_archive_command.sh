#!/usr/bin/env bash
# Archive wrapper emits neutral operation facts for public history.
set -euo pipefail

route=standard
if [[ "${1:-}" == --route=* ]]; then
    route="${1#--route=}"
    shift
fi

source_path="${1:?archive source path is required}"
wal_name="${2:?archive WAL name is required}"
repository=/aiopsbench/archive
delay=0
event_log="${repository}/.aiopsbench-operation-events.jsonl"
started_ms="$(date +%s%3N)"
status=failed

write_event() {
    local finished_ms bytes sha256 durability
    finished_ms="$(date +%s%3N)"
    bytes=0
    sha256=""
    durability=failed
    if [[ "${status}" == success && -f "${repository}/${wal_name}" ]]; then
        bytes="$(stat -c '%s' "${repository}/${wal_name}")"
        sha256="$(sha256sum "${repository}/${wal_name}" | awk '{print $1}')"
        durability=persisted
    fi
    printf '{"timestamp_ms":%s,"event_type":"archive_attempt","entity_type":"repository","entity":"archive_repository","action":"archive","status":"%s","correlation_id":"archive-%s-%s","details":{"route":"%s","segment":"%s","start_ms":%s,"end_ms":%s,"bytes":%s,"durability_result":"%s","sha256":"%s"}}\n' \
        "${finished_ms}" "${status}" "${wal_name}" "${started_ms}" "${route}" "${wal_name}" "${started_ms}" "${finished_ms}" "${bytes}" "${durability}" "${sha256}" \
        >> "${event_log}"
}
trap write_event EXIT

if [[ -r "${repository}/.aiopsbench-delay-seconds" ]]; then
    delay="$(<"${repository}/.aiopsbench-delay-seconds")"
fi
case "${delay}" in
    ''|*[!0-9]*)
        echo "invalid archive delay: ${delay}" >&2
        exit 2
        ;;
esac

fail_next_file="${repository}/.aiopsbench-fail-next"
if [[ -r "${fail_next_file}" ]]; then
    fail_next="$(<"${fail_next_file}")"
    case "${fail_next}" in
        ''|*[!0-9]*)
            fail_next=0
            ;;
    esac
    if (( fail_next > 0 )); then
        printf '%s\n' "$((fail_next - 1))" > "${fail_next_file}"
        echo "archive retry requested" >&2
        exit 75
    fi
fi

sleep "${delay}"
if [[ ! -e "${repository}/${wal_name}" ]]; then
    if [[ "${route}" == "emergency" ]]; then
        # The emergency route relays the segment through a rate-limited
        # transmission tier: chunked copy with an inter-chunk pause sized so
        # the route keeps up with the idle segment cadence but cannot sustain
        # the certification replay burst. The partial file is staged and moved
        # into place atomically so a retry never observes a torn segment.
        staging_path="${repository}/${wal_name}.partial"
        rm -f "${staging_path}"
        chunk_bytes=1048576
        total_bytes="$(stat -c '%s' "${source_path}")"
        offset=0
        while (( offset < total_bytes )); do
            dd if="${source_path}" of="${staging_path}" bs="${chunk_bytes}" \
                skip=$((offset / chunk_bytes)) seek=$((offset / chunk_bytes)) \
                count=1 conv=notrunc status=none
            offset=$((offset + chunk_bytes))
            sleep 0.25
        done
        mv -- "${staging_path}" "${repository}/${wal_name}"
    else
        cp -- "${source_path}" "${repository}/${wal_name}"
    fi
fi
status=success
