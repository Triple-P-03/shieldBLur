"""Show stage-one redaction with clearly synthetic demo values."""

from app.core.guard import ClipboardGuardService


def main() -> None:
    guard = ClipboardGuardService()
    examples = (
        "plain text stays unchanged",
        "copy this synthetic value: AKIA1234567890ABCDEF",
        "service_token=v7Nq2Lm9Qx4Rz8TpK3",
    )
    for source in examples:
        result = guard.process_text(source)
        print(f"IN : {source}")
        print(f"OUT: {result.output_text}")
        print()


if __name__ == "__main__":
    main()
