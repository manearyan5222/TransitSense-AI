"""
TransitSense AI: Automated High-Definition Demo Video Generator
Uses Playwright (Edge Async) and FFmpeg to record a comprehensive 2.5-minute walkthrough
of all 7 platform pages for hackathon submission portals.
"""

import os
import sys
import time
import glob
import asyncio
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DemoRecorder")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "demo_artifacts")
RAW_VIDEO_DIR = os.path.join(OUTPUT_DIR, "raw_video")
FINAL_VIDEO_PATH = os.path.join(PROJECT_ROOT, "TransitSense_AI_Demo.mp4")
THUMBNAIL_PATH = os.path.join(PROJECT_ROOT, "TransitSense_AI_Demo_Thumbnail.png")

os.makedirs(RAW_VIDEO_DIR, exist_ok=True)


def ensure_server_running():
    """Checks if server is responding; if not, starts it."""
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=2) as res:
            if res.status == 200:
                logger.info("Server is already running and healthy.")
                return None
    except Exception:
        pass

    logger.info("Starting local backend server process...")
    cmd = [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4.0)
    return proc


async def smooth_scroll(page, distance, steps=12, delay=0.04):
    """Performs smooth incremental page scrolling."""
    step_dist = distance / steps
    for _ in range(steps):
        await page.evaluate(f"window.scrollBy({{ top: {step_dist}, behavior: 'smooth' }});")
        await asyncio.sleep(delay)


async def record_walkthrough():
    from playwright.async_api import async_playwright

    logger.info("Cleaning previous raw video captures...")
    for f in glob.glob(os.path.join(RAW_VIDEO_DIR, "*.*")):
        try:
            os.remove(f)
        except Exception:
            pass

    logger.info("Ensuring local backend server is running on http://127.0.0.1:8000...")
    server_proc = ensure_server_running()

    try:
        logger.info("Launching Playwright with Microsoft Edge in 1920x1080 resolution...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                channel="msedge",
                headless=True,
                args=[
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--hide-scrollbars"
                ]
            )

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                record_video_dir=RAW_VIDEO_DIR,
                record_video_size={"width": 1920, "height": 1080}
            )

            page = await context.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})

            logger.info("Opening TransitSense AI at http://127.0.0.1:8000/...")
            await page.goto("http://127.0.0.1:8000/", wait_until="networkidle")
            await asyncio.sleep(3.0)

            # -------------------------------------------------------------
            # SCENE 1: OVERVIEW & LANDING HERO (18 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 1: Overview Page & Network Telemetry...")
            await page.mouse.move(500, 300)
            await asyncio.sleep(3.0)

            # Smooth scroll down to reveal KPIs, corridor pulse cards, and Flow Conservation
            await smooth_scroll(page, 450, steps=15, delay=0.06)
            await asyncio.sleep(3.0)

            await smooth_scroll(page, 450, steps=15, delay=0.06)
            await asyncio.sleep(4.0)

            # Scroll back up to the header
            await smooth_scroll(page, -900, steps=15, delay=0.05)
            await asyncio.sleep(2.0)

            # -------------------------------------------------------------
            # SCENE 2: DATA PROVENANCE & SCIENTIFIC DISCLOSURE MODAL (12 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 2: Data Provenance Modal...")
            provenance_btn = page.locator("text=DATA: SYNTHETIC DEMO")
            if await provenance_btn.count() > 0:
                await provenance_btn.first.click()
                await asyncio.sleep(3.5)
                await page.mouse.move(960, 540)
                await asyncio.sleep(3.0)
                close_btn = page.locator("button:has-text('Acknowledge & Close'), button:has-text('✕')")
                if await close_btn.count() > 0:
                    await close_btn.first.click()
                await asyncio.sleep(2.0)

            # -------------------------------------------------------------
            # SCENE 3: MULTI-OBJECTIVE JOURNEY PLANNER (35 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 3: Journey Planner...")
            await page.locator("button:has-text('Journey Planner')").first.click()
            await asyncio.sleep(2.5)

            # Show input form and pre-selected Anand Vihar -> Mehrauli
            await smooth_scroll(page, 200, steps=10, delay=0.05)
            await asyncio.sleep(2.0)

            # Click submit button
            submit_btn = page.locator("button[type='submit']")
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
                await asyncio.sleep(3.0)  # Wait for ML inference and map rendering

            # Smooth scroll to show AI Recommendation Analysis and Itinerary Options
            await smooth_scroll(page, 300, steps=12, delay=0.06)
            await asyncio.sleep(3.5)

            # Toggle to Comfort-First routing
            least_crowded_btn = page.locator("text=Least Crowded")
            if await least_crowded_btn.count() > 0:
                await least_crowded_btn.first.click()
                await asyncio.sleep(1.5)
                await submit_btn.first.click()
                await asyncio.sleep(3.0)

            # Expand stop-by-stop passenger loads table
            details_elem = page.locator("summary:has-text('View stop-by-stop passenger loads')")
            if await details_elem.count() > 0:
                await details_elem.first.click()
                await asyncio.sleep(2.0)
                await page.mouse.move(500, 650)
                await asyncio.sleep(2.5)

            # Scroll down slightly to admire map and table side by side
            await smooth_scroll(page, 200, steps=8, delay=0.06)
            await asyncio.sleep(3.5)

            # Scroll back up
            await smooth_scroll(page, -700, steps=12, delay=0.05)
            await asyncio.sleep(1.5)

            # -------------------------------------------------------------
            # SCENE 4: CORRIDOR ROUTE COMPARISON (18 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 4: Route Comparison...")
            await page.locator("button:has-text('Route Comparison')").first.click()
            await asyncio.sleep(3.0)

            await smooth_scroll(page, 350, steps=12, delay=0.06)
            await asyncio.sleep(3.5)
            await page.mouse.move(600, 450)
            await asyncio.sleep(3.0)
            await smooth_scroll(page, -350, steps=10, delay=0.05)
            await asyncio.sleep(1.5)

            # -------------------------------------------------------------
            # SCENE 5: CROWD INTELLIGENCE & 24-HOUR DIURNAL CURVES (18 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 5: Crowd Intelligence & Diurnal Curves...")
            await page.locator("button:has-text('Crowd Intelligence')").first.click()
            await asyncio.sleep(3.0)

            # Hover over the Chart.js canvas
            await smooth_scroll(page, 250, steps=10, delay=0.06)
            await page.mouse.move(700, 500)
            await asyncio.sleep(4.0)

            # Switch route to Route 764 (Najafgarh -> Nehru Place)
            route_select = page.locator("select").first
            if await route_select.count() > 0:
                await route_select.select_option(value="DTC_764")
                await asyncio.sleep(1.5)
                eval_btn = page.locator("button:has-text('Evaluate ML Model')")
                if await eval_btn.count() > 0:
                    await eval_btn.first.click()
                await asyncio.sleep(3.5)

            await smooth_scroll(page, -250, steps=10, delay=0.05)
            await asyncio.sleep(1.5)

            # -------------------------------------------------------------
            # SCENE 6: INTERACTIVE DELHI MAP (22 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 6: Interactive Delhi Network Map...")
            await page.locator("button:has-text('Delhi Network Map')").first.click()
            await asyncio.sleep(3.0)

            # Pan on map
            await page.mouse.move(800, 450)
            await asyncio.sleep(2.0)

            # Click Evening Peak preset
            eve_btn = page.locator("button:has-text('Evening Peak')")
            if await eve_btn.count() > 0:
                await eve_btn.first.click()
                await asyncio.sleep(3.0)

            # Click Midday preset
            mid_btn = page.locator("button:has-text('Midday')")
            if await mid_btn.count() > 0:
                await mid_btn.first.click()
                await asyncio.sleep(2.5)

            # Filter by Route 534
            r534_btn = page.locator("button:has-text('Route 534')")
            if await r534_btn.count() > 0:
                await r534_btn.first.click()
                await asyncio.sleep(2.5)

            # Restore All Corridors
            all_btn = page.locator("button:has-text('All Corridors')")
            if await all_btn.count() > 0:
                await all_btn.first.click()
                await asyncio.sleep(2.5)

            # -------------------------------------------------------------
            # SCENE 7: WHAT-IF SIMULATOR (18 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 7: What-If Journey Simulator...")
            await page.locator("button:has-text('What-If Simulator')").first.click()
            await asyncio.sleep(3.0)

            await smooth_scroll(page, 200, steps=10, delay=0.05)
            await asyncio.sleep(2.0)

            # Click +15m departure shift
            shift_btn = page.locator("button:has-text('+15m')")
            if await shift_btn.count() > 0:
                await shift_btn.first.click()
                await asyncio.sleep(2.5)

            # Toggle to Electric AC bus (46 pax)
            ev_btn = page.locator("button:has-text('Electric AC (46 Pax)')")
            if await ev_btn.count() > 0:
                await ev_btn.first.click()
                await asyncio.sleep(2.5)

            # Select Monsoon Rain (+25%) surge if select exists
            surge_selects = page.locator("select")
            if await surge_selects.count() > 1:
                await surge_selects.nth(1).select_option(value="1.25")
                await asyncio.sleep(3.0)

            await smooth_scroll(page, 250, steps=10, delay=0.05)
            await asyncio.sleep(3.0)

            await smooth_scroll(page, -450, steps=12, delay=0.05)
            await asyncio.sleep(1.5)

            # -------------------------------------------------------------
            # SCENE 8: MODEL & ANALYTICS DASHBOARD (20 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 8: Model & Analytics Dashboard...")
            await page.locator("button:has-text('Model & Analytics')").first.click()
            await asyncio.sleep(3.0)

            await smooth_scroll(page, 400, steps=15, delay=0.06)
            await asyncio.sleep(4.0)

            # Scroll to show ML benchmark comparison table and scientific disclosure
            await smooth_scroll(page, 450, steps=15, delay=0.06)
            await asyncio.sleep(4.5)

            await smooth_scroll(page, -850, steps=15, delay=0.05)
            await asyncio.sleep(2.0)

            # -------------------------------------------------------------
            # SCENE 9: FINALE / RETURN TO JOURNEY PLANNER HERO (10 seconds)
            # -------------------------------------------------------------
            logger.info("Recording Scene 9: Finale...")
            await page.locator("button:has-text('Journey Planner')").first.click()
            await asyncio.sleep(2.5)
            await smooth_scroll(page, 300, steps=10, delay=0.05)
            await asyncio.sleep(3.5)

            logger.info("Finalizing browser recording context...")
            await page.close()
            await context.close()
            await browser.close()

    finally:
        if server_proc:
            try:
                server_proc.terminate()
                server_proc.wait(timeout=3)
            except Exception:
                pass

    # Find recorded webm file
    recorded_files = glob.glob(os.path.join(RAW_VIDEO_DIR, "*.webm")) + glob.glob(os.path.join(RAW_VIDEO_DIR, "*.mp4"))
    if not recorded_files:
        raise RuntimeError("No video file was output by Playwright.")

    raw_video = recorded_files[0]
    logger.info(f"Raw video recorded: {raw_video} ({os.path.getsize(raw_video)/1024/1024:.2f} MB)")

    # -------------------------------------------------------------
    # POST-PROCESSING VIA FFMPEG
    # -------------------------------------------------------------
    logger.info(f"Encoding high-definition production MP4 via FFmpeg -> {FINAL_VIDEO_PATH}...")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        FINAL_VIDEO_PATH
    ]

    subprocess.run(ffmpeg_cmd, check=True)
    logger.info(f"Final demo video ready: {FINAL_VIDEO_PATH} ({os.path.getsize(FINAL_VIDEO_PATH)/1024/1024:.2f} MB)")

    # Extract clean 1080p thumbnail at 28s mark
    logger.info(f"Generating high-resolution thumbnail -> {THUMBNAIL_PATH}...")
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:28",
        "-i", FINAL_VIDEO_PATH,
        "-vframes", "1",
        "-q:v", "2",
        THUMBNAIL_PATH
    ]
    subprocess.run(thumb_cmd, check=True)
    logger.info("Thumbnail generated successfully.")

    return FINAL_VIDEO_PATH, THUMBNAIL_PATH


if __name__ == "__main__":
    asyncio.run(record_walkthrough())
