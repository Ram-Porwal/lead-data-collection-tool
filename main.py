from pathlib import Path

from lead_collector.config import Settings
from lead_collector.discovery.serpapi import SerpApiDiscoveryProvider
from lead_collector.export.csv_exporter import CSVLeadExporter
from lead_collector.export.excel_exporter import ExcelLeadExporter
from lead_collector.pipeline import LeadCollectionPipeline
from lead_collector.storage.database import LeadDatabase


def main() -> None:
    print("=" * 50)
    print("       Lead Data Collection Tool")
    print("=" * 50)
    print()

    query = input("Enter search query: ").strip()

    if not query:
        print("Error: Search query cannot be empty.")
        return

    max_results_input = input(
        "Maximum results [10]: "
    ).strip()

    if max_results_input:
        try:
            max_results = int(max_results_input)
        except ValueError:
            print("Error: Maximum results must be a number.")
            return

        if max_results <= 0:
            print("Error: Maximum results must be greater than 0.")
            return
    else:
        max_results = 10

    output_dir = Path("data/exports")
    database_path = Path("data/processed/leads.db")

    csv_path = output_dir / "leads.csv"
    excel_path = output_dir / "leads.xlsx"

    try:
        settings = Settings()

        discovery_provider = SerpApiDiscoveryProvider(settings)

        database = LeadDatabase(database_path)

        pipeline = LeadCollectionPipeline(
            discovery_provider=discovery_provider,
            database=database,
            csv_exporter=CSVLeadExporter(),
            excel_exporter=ExcelLeadExporter(),
        )

        print()
        print("Starting lead collection...")
        print()

        result = pipeline.run(
            query,
            max_results=max_results,
            csv_path=csv_path,
            excel_path=excel_path,
        )

    except Exception as error:
        print()
        print(f"Error: {error}")
        return

    valid_leads = [
        lead
        for lead in result.leads
        if lead.validation_status.value == "valid"
    ]

    print()
    print("=" * 50)
    print("             Collection Complete")
    print("=" * 50)
    print()
    print(f"Discovered results       : {result.discovered}")
    print(f"Rejected by quality      : {result.rejected_by_quality}")
    print(f"Unique accepted results : {result.unique_results}")
    print(f"Websites fetched        : {result.fetched}")
    print(f"Failed fetches     : {result.failed_fetches}")
    print(f"Leads collected    : {len(result.leads)}")
    print(f"Valid leads        : {len(valid_leads)}")
    print()
    print("Output files:")
    print(f"SQLite : {database_path}")
    print(f"CSV    : {csv_path}")
    print(f"Excel  : {excel_path}")
    print()


if __name__ == "__main__":
    main()