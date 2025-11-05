# files/processing.py
from fastapi import UploadFile
from typing import Dict
from files.logger import logger
from files.AImodels import AIModules

class DataProcessor:
    def __init__(self):
        self.version = "0.0.1"
        self.module_name = "DataProcessor"
        self.ai_modules = AIModules()
        logger.info(f"{self.module_name} initialized (v{self.version})")

    def info(self) -> dict:
        return {"module_name": self.module_name, "version": self.version}

    async def process_input(
        self,
        name: str,
        roll: str,
        image: UploadFile
    ) -> Dict:
        try:
            # Validate image type
            if image.content_type not in ("image/jpeg", "image/png"):
                raise ValueError(f"Unsupported image type: {image.content_type}")

            # Read bytes (we keep bytes for both ML and DB)
            image_bytes = await image.read()
            logger.info(f"{self.module_name}: read image for roll={roll}, size={len(image_bytes)} bytes")

            # Step 1: Liveliness
            await self.ai_modules.check_liveliness(roll, image_bytes)
            logger.info(f"{self.module_name}: liveliness check passed for roll={roll}")

            # Step 2: Embeddings
            embedding = await self.ai_modules.create_embeddings(roll, image_bytes)
            logger.info(f"{self.module_name}: embeddings created for roll={roll}")

            # Step 3: Optional match (not necessary on submit)
            # await self.ai_modules.match_face(roll, image_bytes)

            user_data = {
                "name": name.strip(),
                "roll": roll.strip(),
                "image_data": image_bytes,   # raw bytes
                "embedding": embedding       # list[float]
            }

            logger.info(f"{self.module_name}: processing complete for roll={roll}")
            return user_data

        except Exception as e:
            logger.error(f"{self.module_name} failed processing input for roll={roll}: {e}")
            raise e
