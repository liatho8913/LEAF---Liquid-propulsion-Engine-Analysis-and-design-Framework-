from foundation_layer_controller import FoundationLayerController


def main():
    controller = FoundationLayerController(
        get_benchmark_case_callback=lambda: "Merlin_1D",
        get_startup_health_callback=lambda: {},
    )

    result = controller.run_foundation_verification()

    print(result.get("foundation_verification_text", "No report generated."))

    if result.get("foundation_final_signoff_complete"):
        print("\nLEAF Foundation Layer Verified")
        print("LEAF Final Foundation Sign-Off Complete")
    else:
        print("\nLEAF Foundation Layer NOT Verified")
        print("LEAF Final Foundation Sign-Off NOT Complete")
        print(result.get("foundation_final_signoff_status", "UNKNOWN"))

    print(result.get(
        "foundation_completion_handover_status",
        "No foundation completion handover status available.",
    ))

    if result.get("foundation_completion_handover_ready_for_regen_geometry"):
        print("LEAF is ready for Regen Geometry Completion Phase 1")
    else:
        print("LEAF is NOT ready for Regen Geometry Completion Phase 1")

if __name__ == "__main__":
    main()