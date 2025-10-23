import aiofiles
from aiocsv import AsyncDictReader, AsyncWriter


async def read_csv(filepath: str) -> list[dict]:
    """Читаем данные из CSV-файла."""
    data = []
    async with aiofiles.open(
        filepath, mode='r', encoding='utf-8-sig', newline=''
    ) as csvfile:
        async for row in AsyncDictReader(csvfile, delimiter=';'):
            data.append(row)
    return data


async def write_csv(data: list[tuple], filepath: str) -> None:
    """Записываем данные в CSV-файл."""
    async with aiofiles.open(
        filepath, mode='w', encoding='utf-8-sig', newline=''
    ) as csvfile:
        writer = AsyncWriter(csvfile, delimiter=';')
        await writer.writerows(data)
