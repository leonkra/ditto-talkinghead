import logging
import os
import platform
import subprocess
import sys
import tarfile
import urllib.request


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
logger.addHandler(stdout_handler)


def download_ffmpeg():
    system = platform.system().lower()

    if system == "linux":
        logger.info("Detected Linux. Installing ffmpeg...")
        url = "https://rpm.repo.local.sfdc.net/artifactory/strata-blobs/baas/ffmpeg-git-amd64-static.tar.xz"
        output_archive = "ffmpeg-release-amd64-static.tar.xz"

        logger.info(f"Downloading ffmpeg from {url}...")
        urllib.request.urlretrieve(url, output_archive)

        logger.info(f"Extracting {output_archive}...")
        with tarfile.open(output_archive, "r:xz") as tar_ref:
            tar_ref.extractall("ffmpeg")

        subprocess.run(["mv", "ffmpeg/ffmpeg-git-amd64-static/ffmpeg", "/usr/bin"], check=True)
        subprocess.run(["mv", "ffmpeg/ffmpeg-git-amd64-static/ffprobe", "/usr/bin"], check=True)

        os.remove(output_archive)
        logger.info(f"ffmpeg installed successfully in the '/usr/bin' directory")

    elif system == "darwin":
        logger.info("Detected macOS. Checking if ffmpeg is installed via Homebrew...")
        try:
            subprocess.run(["brew", "list", "ffmpeg"], check=True)
            logger.info("ffmpeg is already installed via Homebrew.")
        except subprocess.CalledProcessError:
            logger.info("ffmpeg is not installed. Installing via Homebrew...")
            try:
                subprocess.run(["brew", "install", "ffmpeg"], check=True)
                logger.info("ffmpeg installed successfully via Homebrew.")
            except subprocess.CalledProcessError as e:
                logger.info(f"Failed to install ffmpeg via Homebrew: {e}")
                sys.exit(1)
        except FileNotFoundError:
            logger.info(
                "Homebrew is not installed. Please install Homebrew and run the script again."
            )
            sys.exit(1)

    else:
        raise ValueError(f"Unsupported platform: {system}")


if __name__ == "__main__":
    download_ffmpeg()
