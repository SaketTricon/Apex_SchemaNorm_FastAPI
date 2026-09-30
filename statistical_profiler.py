"""Command-line entry point for the statistical profiling service."""

from app.services.statistical_profiler import main


if __name__ == "__main__":
    raise SystemExit(main())
