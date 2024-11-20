export async function calculateCRC32(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const view = new Uint8Array(buffer);
  let crc = 0xFFFFFFFF;
  
  for (let i = 0; i < view.length; i++) {
    crc ^= view[i];
    for (let j = 0; j < 8; j++) {
      crc = (crc >>> 1) ^ ((crc & 1) ? 0xEDB88320 : 0);
    }
  }
  
  return (crc ^ 0xFFFFFFFF >>> 0).toString(16).padStart(8, '0');
}