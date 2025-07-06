    async saveChunksToFiles(outputDir: string, chunkSamples: number): Promise<void> {
        let chunkIndex = 0;
        let chunk: Uint8Array | Int16Array | null;

        while ((chunk = await this.readNext(chunkSamples)) !== null) {
            const fileName = path.join(outputDir, `chunk_${chunkIndex.toString().padStart(5, '0')}.raw`);
            const buffer = chunk instanceof Int16Array
                ? Buffer.from(new Uint8Array(chunk.buffer, chunk.byteOffset, chunk.byteLength))
                : Buffer.from(chunk);
            await writeFile(fileName, buffer);
            chunkIndex++;
        }
    }

// 🔽 Save chunks while reading
                const outputDir = path.join(path.dirname(filename), 'chunks');
                await mkdir(outputDir, { recursive: true });
                const chunkSamples = 160;
                let index = 0;
                let chunkData: Uint8Array | Int16Array | null;
                while ((chunkData = await reader.readNext(chunkSamples)) !== null) {
                    const buffer = chunkData instanceof Int16Array
                        ? Buffer.from(new Uint8Array(chunkData.buffer, chunkData.byteOffset, chunkData.byteLength))
                        : Buffer.from(chunkData);
                    const outPath = path.join(outputDir, `chunk_${index.toString().padStart(5, '0')}.raw`);
                    await writeFile(outPath, buffer);
                    index++;
                }

                await reader.close(); // optional
