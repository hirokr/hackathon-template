import 'dotenv/config';
import { UTApi } from 'uploadthing/server';
import fs from 'node:fs/promises';

const utapi = new UTApi();

type UploadResult = Awaited<ReturnType<typeof utapi.uploadFilesFromUrl>>;

export async function handleUrlUpload(
  productUrl: string,
  fileName: string
): Promise<UploadResult> {
  const normalizedName = fileName.endsWith('.png')
    ? fileName
    : `${fileName}.png`;

  const response = await utapi.uploadFilesFromUrl({
    url: productUrl,
    name: normalizedName,
  });
  return [response];
}

export async function handleFileUpload(
  fileName: string,
  filePath: string
): Promise<UploadResult> {
  const buffer = await fs.readFile(filePath);

  // Ensure .png extension in filename
  const normalizedName = fileName.endsWith('.png')
    ? fileName
    : `${fileName}.png`;
  const file = new File([buffer], normalizedName, { type: 'image/png' });

  const response = await utapi.uploadFiles(file);
  return [response];
}

// handleUrlUpload(
//   'https://avatars.githubusercontent.com/u/117710065?v=4',
//   'profile-image.png'
// );
