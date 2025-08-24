from nicegui import ui
from defines import BUS_GOV_LANGUAGE_HEBREW, BUS_GOV_LANGUAGE_ENGLISH
from bus_gov_scraper import GovILBusStopScraper
from yaml_config_loader import getBusFilterConfig
from concurrent.futures import ThreadPoolExecutor, Future

GRID_COLUMNS = 2
GRID_ROWS = 2
UI_REFRESH_TIME_SECONDS = 15
MAX_THREADS = 128
CARD_HEADER_ROW_SIZE = 2.5
MAX_ROWS_PER_SLIDE = 11

def busDisplayUi(scraper: GovILBusStopScraper):
    with ui.card().tight() as card:
        card.classes("items-center")
        card.classes("w-full h-full")
        card.props("flat bordered")
        card.style("background-color: #2b323b")
        ui.label(scraper.stopName).classes("text-cs font-bold text-center w-full").style("color: #A5D6FF;")
        ui.label(scraper.stopCode).classes("text-cs font-bold text-center w-full").style("color: #A5D6FF;")

        columns = [
            {"name": "operator", "label": "Operator", "field": "operator", "required": True, "align": "left"},
            {"name": "route", "label": "Route", "field": "route", "required": True, "align": "left"},
            {"name": "arrivals", "label": "Arrivals", "field": "arrivals", "required": True, "align": "left"},
        ]

        rows = list(scraper.getScrapedData())

        table = ui.table(columns=columns, rows=rows, row_key="name")
        table.classes("w-full h-full")
        table.style("background-color: #181c21; color: #A5D6FF;")
        table.props("dense")

def addCarouselSlide(futures: list[tuple:[Future, GovILBusStopScraper]], start, stop):
    with ui.carousel_slide().classes("p-0"): 
        with ui.grid(columns=GRID_COLUMNS) as grid:
            grid.classes("w-full h-full gap-0.5")
            for i in range(start, stop + 1):
                (_, scraper) = futures[i]
                busDisplayUi(scraper)

@ui.refreshable
def busDisplaySlideshowUI(scrapers: list[GovILBusStopScraper]):
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for scraper in scrapers:
            futures.append((executor.submit(GovILBusStopScraper.scrape, *[scraper]), scraper))

    for (future, scraper) in futures:
        future.result()

    with ui.carousel(animated=True, arrows=True) as carousel:
        carousel.style("background-color: #1d1d1d")
        carousel.classes("w-full h-full")
        carousel.props("autoplay")

        start = stop = 0
        totalSlideRows = 0
        maxRow = -1
        for (index, (future, scraper)) in enumerate(futures):
            if index % 2 == 0:
                maxRow = len(scraper.getScrapedData())
            else:
                maxRow = max(maxRow, len(scraper.getScrapedData()))

                # Empty Data is filled with
                # a "No data available" row
                if maxRow == 0:
                    maxRow = 1
                maxRow += CARD_HEADER_ROW_SIZE

                if maxRow + totalSlideRows > MAX_ROWS_PER_SLIDE:
                    stop = index - 2
                    addCarouselSlide(futures, start, stop)
                    totalSlideRows = maxRow
                    start = stop = index - 1
                elif maxRow + totalSlideRows == MAX_ROWS_PER_SLIDE:
                    stop = index 
                    addCarouselSlide(futures, start, stop)
                    totalSlideRows = 0
                    start = stop = index + 1
                else:
                    totalSlideRows += maxRow

        if start < index:
            # Add the leftover 
            # data to a slide
            if index % 2 == 0:
                # Empty Data is filled with
                # a "No data available" row
                if maxRow == 0:
                    maxRow = 1
                maxRow += CARD_HEADER_ROW_SIZE

                if maxRow + totalSlideRows > MAX_ROWS_PER_SLIDE:
                    stop = index - 1
                    addCarouselSlide(futures, start, stop)
                    addCarouselSlide(futures, index, index)
                elif maxRow + totalSlideRows <= MAX_ROWS_PER_SLIDE:
                    stop = index 
                    addCarouselSlide(futures, start, stop)
            else:
                stop = index
                addCarouselSlide(futures, start, stop)

def initScrappers():
    STOP_CODE_INDEX = 0
    FILTER_CONFIG_INDEX = 1

    scrapers = []
    config = getBusFilterConfig()
    
    if config is not None:
        language = config[0]
        for filterConfig in config[1:]:
            scrapers.append(GovILBusStopScraper(filterConfig[STOP_CODE_INDEX], filterConfig[FILTER_CONFIG_INDEX], language))
    
    return scrapers

def set_background(color: str) -> None:
    ui.query("body").style(f"background-color: {color}")

def main():
    scrapers = initScrappers()
    if scrapers:
        ui.query(".nicegui-content").classes("p-0.5")
        busDisplaySlideshowUI(scrapers)
        
        set_background("#1d1d1d")
        ui.timer(UI_REFRESH_TIME_SECONDS, busDisplaySlideshowUI.refresh, immediate=False)
        ui.run()
    else:
        print("Error Initialising")  

if __name__ in {"__main__", "__mp_main__"}:
    main()
