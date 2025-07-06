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
