import fitz
# from pathlib import Path

from utils.logger import logger


class ImageExtractor:

    # @staticmethod
    # def extract(pdf: fitz.Document, recipe_id: str, image_dir: Path) -> str | None:
    #     """Legacy method - kept for compatibility."""
    #     image_dir.mkdir(parents=True, exist_ok=True)

    #     image_path = image_dir / f"{recipe_id}.jpg"

    #     for page in pdf:
    #         images = page.get_images(full=True)
    #         if not images:
    #             continue

    #         xref = images[0][0]
    #         pix = fitz.Pixmap(pdf, xref)

    #         if pix.alpha:
    #             pix = fitz.Pixmap(fitz.csRGB, pix)

    #         pix.save(image_path)
    #         logger.info("Extracted image for recipe %s", recipe_id)
    #         return image_path.name

    #     return None
    
    @staticmethod
    def extract_main_image(
        pdf: fitz.Document,
        recipe_id: str,
    ) -> dict | None:

        best_data = None
        best_size = 0
        best_ext = "jpg"

        for page_num, page in enumerate(pdf):
            images = page.get_images(full=True)

            for img_info in images:
                try:
                    xref = img_info[0]

                    img_dict = pdf.extract_image(xref)

                    if not img_dict or not img_dict.get("image"):
                        continue

                    data = img_dict["image"]
                    size = len(data)

                    if size > best_size:
                        best_size = size
                        best_data = data
                        best_ext = img_dict.get(
                            "ext",
                            "jpg"
                        ).lower()

                except Exception as e:
                    logger.debug(
                        "Image extraction failed on page %d: %s",
                        page_num,
                        e,
                    )

        # fallback scan
        if not best_data:

            logger.debug(
                "Trying full xref scan fallback for recipe %s",
                recipe_id
            )

            for xref in range(1, pdf.xref_length()):

                try:
                    img_dict = pdf.extract_image(xref)

                    if img_dict and img_dict.get("image"):

                        data = img_dict["image"]

                        if len(data) > best_size:
                            best_size = len(data)
                            best_data = data
                            best_ext = img_dict.get(
                                "ext",
                                "jpg"
                            ).lower()

                except Exception:
                    continue


        if not best_data:
            logger.warning(
                "No images found in PDF for recipe %s",
                recipe_id
            )
            return None


        filename = f"{recipe_id}.{best_ext}"


        logger.info(
            "Extracted image: %s (%d bytes)",
            filename,
            best_size,
        )


        return {
            "filename": filename,
            "bytes": best_data,
            "extension": best_ext,
        }

    # @staticmethod
    # def extract_main_image(
    #     pdf: fitz.Document, 
    #     recipe_id: str, 
    #     image_dir: Path
    # ) -> str | None:
    #     image_dir.mkdir(parents=True, exist_ok=True)

    #     best_data = None
    #     best_size = 0
    #     best_ext = "jpg"

    #     for page_num, page in enumerate(pdf):
    #         images = page.get_images(full=True)
    #         for img_info in images:
    #             try:
    #                 xref = img_info[0]
    #                 img_dict = pdf.extract_image(xref)
    #                 if not img_dict or not img_dict.get("image"):
    #                     continue

    #                 data = img_dict["image"]
    #                 size = len(data)

    #                 if size > best_size:
    #                     best_size = size
    #                     best_data = data
    #                     best_ext = img_dict.get("ext", "jpg").lower()
    #             except Exception as e:
    #                 logger.debug("Image extraction failed on page %d: %s", page_num, e)

    #     if not best_data:
    #         logger.debug("Trying full xref scan fallback for recipe %s", recipe_id)
    #         for xref in range(1, pdf.xref_length()):
    #             try:
    #                 img_dict = pdf.extract_image(xref)
    #                 if img_dict and img_dict.get("image"):
    #                     data = img_dict["image"]
    #                     if len(data) > best_size:
    #                         best_size = len(data)
    #                         best_data = data
    #                         best_ext = img_dict.get("ext", "jpg").lower()
    #             except:
    #                 continue

    #     if not best_data:
    #         logger.warning("No images found in PDF for recipe %s", recipe_id)
    #         return None

    #     filename = f"{recipe_id}.{best_ext}"
    #     image_path = image_dir / filename

    #     with open(image_path, "wb") as f:
    #         f.write(best_data)

    #     logger.info("Saved image: %s (%d bytes)", filename, best_size)
    #     return filename