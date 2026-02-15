import loguru
import aiohttp
import asyncio
from pathlib import Path

from bot.models.context import JobContext
from bot.config.settings import settings
from bot.exceptions import ProcessingError

# Auphonic status codes:
# {
#     "status_code": 200,
#     "error_code": null,
#     "error_message": "",
#     "form_errors": {},
#     "data": {
#         "0": "File Upload",
#         "1": "Waiting",
#         "2": "Error",
#         "3": "Done",
#         "4": "Audio Processing",
#         "5": "Audio Encoding",
#         "6": "Outgoing File Transfer",
#         "7": "Audio Mono Mixdown",
#         "8": "Split Audio On Chapter Marks",
#         "9": "Incomplete",
#         "10": "Production Not Started Yet",
#         "11": "Production Outdated",
#         "12": "Incoming File Transfer",
#         "13": "Stopping the Production",
#         "14": "Speech Recognition",
#         "15": "Production Changed"
#     }
# }


class AiProcessor:

    async def process(self, ctx: JobContext):

        if not ctx.voice_path:
            raise ProcessingError("voice_not_found")

        headers = {
            "Authorization": f"Bearer {settings.AUPHONIC_API_KEY}"
        }

        input_path = ctx.voice_path

        async with aiohttp.ClientSession() as session:
            with open(input_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("input_file", f)

                # Output configuration (no preset)
                data.add_field("output_files", '[{"format":"mp3","bitrate":"192"}]')
                data.add_field("loudness_target", "-16")
                data.add_field("denoise", "true")
                data.add_field("leveler", "true")

                async with session.post(
                    "https://auphonic.com/api/simple/productions.json",
                    headers=headers,
                    data=data,
                ) as resp:

                    if resp.status != 200:
                        text = await resp.text()
                        loguru.logger.error(
                            f"Auphonic upload failed: {resp.status} | {text}"
                        )
                        raise ProcessingError("auphonic_upload_failed")

                    result = await resp.json()
                    production_uuid = result["data"]["uuid"]

            start_url = f"https://auphonic.com/api/production/{production_uuid}/start.json"
            async with session.post(start_url, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    loguru.logger.error(
                        f"Auphonic start failed: {resp.status} | {text}"
                    )
                    raise ProcessingError("auphonic_start_failed")

            status_url = f"https://auphonic.com/api/production/{production_uuid}.json"

            # Polling
            for _ in range(60):
                await asyncio.sleep(5)

                async with session.get(status_url, headers=headers) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        loguru.logger.error(
                            f"Auphonic status check failed: {resp.status} | {text}"
                        )
                        raise ProcessingError("auphonic_status_failed")

                    data = await resp.json()
                    # loguru.logger.info(
                    #     f"Auphonic status response: {data}"
                    # )
                    status = data["data"]["status"]

                    loguru.logger.info(
                        f"Auphonic processing status: {status} for production {production_uuid}"
                    )

                    # 1 = File Upload
                    if status == 1:
                        ctx.status = "uploading"

                    # 2 = Error 
                    if status == 2:
                        raise ProcessingError("auphonic_processing_failed")

                    # 3 = Done
                    if status == 3:
                        output_url = data["data"]["output_files"][0]["download_url"]
                        return await self._download(session, output_url, ctx, headers)

                    # 4 = Processing
                    if status == 4:
                        ctx.status = "processing"

            raise ProcessingError("auphonic_timeout")

    async def _download(self, session, url: str, ctx: JobContext, headers):

        output_path = Path("storage/processed") / f"{ctx.voice_path.stem}_ai.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                loguru.logger.error(
                    f"Auphonic download failed: {resp.status} | {text}"
                )
                raise ProcessingError("auphonic_download_failed")

            content = await resp.read()
            output_path.write_bytes(content)

        ctx.output_files.append(output_path)

        loguru.logger.info(f"Downloaded processed file to {output_path}")

        return output_path