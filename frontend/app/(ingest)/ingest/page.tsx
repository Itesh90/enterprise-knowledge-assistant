"use client";
import { useIngest, useIngestUpload, useIngestStatus } from '../../../lib/client';
import { Input } from '../../../components/ui/Input';
import { Button } from '../../../components/ui/Button';
import React from 'react';

export default function IngestPage() {
  const [path, setPath] = React.useState('backend/data/raw');
  const [files, setFiles] = React.useState<File[]>([]);
  const [isDragging, setIsDragging] = React.useState(false);
  const { mutateAsync: ingestPath, isPending: isPendingPath } = useIngest();
  const { mutateAsync: ingestUpload, isPending: isPendingUpload } = useIngestUpload();
  const { data: status, refetch: refetchStatus } = useIngestStatus();

  const isPending = isPendingPath || isPendingUpload;

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) => {
      const lower = file.name.toLowerCase();
      return lower.endsWith('.md') || lower.endsWith('.markdown') || lower.endsWith('.pdf') || lower.endsWith('.html') || lower.endsWith('.htm');
    });

    if (droppedFiles.length > 0) {
      setFiles((prev) => [...prev, ...droppedFiles]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []).filter((file) => {
      const lower = file.name.toLowerCase();
      return lower.endsWith('.md') || lower.endsWith('.markdown') || lower.endsWith('.pdf') || lower.endsWith('.html') || lower.endsWith('.htm');
    });

    if (selectedFiles.length > 0) {
      setFiles((prev) => [...prev, ...selectedFiles]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    try {
      const result = await ingestUpload({ files, max_chunk_tokens: 512, overlap: 64 });
      
      // Show detailed success message
      const message = result.status === 'ok' 
        ? `✅ Successfully processed!\n\n` +
          `Files: ${result.files_processed || files.length}\n` +
          `Documents added: ${result.documents_added || 0}\n` +
          `Chunks added: ${result.chunks_added || 0}\n` +
          `Total documents: ${result.total_documents || 0}\n` +
          `Total chunks: ${result.total_chunks || 0}`
        : `⚠️ ${result.status}`;
      
      alert(message);
      setFiles([]);
      // Refresh status to show new documents
      refetchStatus();
    } catch (error) {
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Upload failed'}`);
    }
  };

  return (
    <main className="space-y-6 animate-fade-in">
      <h1 className="text-3xl font-bold gradient-text">📥 Document Ingest</h1>

      {/* Drag and Drop Zone */}
      <div className="glass rounded-xl p-6 shadow-lg space-y-4">
        <h2 className="text-xl font-semibold text-black">📤 Upload Files</h2>
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
            isDragging
              ? 'border-purple-500 bg-gradient-to-br from-purple-50 to-pink-50 scale-105'
              : 'border-purple-300 bg-gradient-to-br from-blue-50 to-purple-50 hover:border-purple-400 hover:bg-gradient-to-br hover:from-purple-50 hover:to-pink-50'
          }`}
        >
          <div className="space-y-4">
            <div className="text-6xl">📎</div>
            <div>
              <p className="text-lg font-medium text-black mb-2">
                {isDragging ? '✨ Drop files here!' : 'Drag and drop files here'}
              </p>
              <p className="text-sm text-gray-600 mb-4">or</p>
              <label className="cursor-pointer">
                <input
                  type="file"
                  multiple
                  accept=".md,.markdown,.pdf,.html,.htm"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <span className="inline-block px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium hover:from-blue-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105">
                  📁 Browse Files
                </span>
              </label>
            </div>
            <p className="text-xs text-gray-500">Supports: .md, .markdown, .pdf, .html, .htm</p>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-black">Selected Files ({files.length}):</h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-white to-blue-50 border border-purple-200 rounded-lg hover:shadow-md transition-all duration-200"
                >
                  <span className="text-sm text-black flex-1 truncate">{file.name}</span>
                  <span className="text-xs text-gray-500 mr-3">{(file.size / 1024).toFixed(1)} KB</span>
                  <button
                    onClick={() => handleRemoveFile(index)}
                    className="px-2 py-1 text-xs rounded bg-red-500 text-white hover:bg-red-600 transition-colors"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
            <Button onClick={handleUpload} disabled={isPending} className="w-full">
              {isPending ? '🔄 Processing...' : `🚀 Upload & Ingest ${files.length} File(s)`}
            </Button>
          </div>
        )}
      </div>

      {/* Directory Path Option */}
      <div className="glass rounded-xl p-6 shadow-lg space-y-4">
        <h2 className="text-xl font-semibold text-black">📂 Or Use Directory Path</h2>
        <div className="flex gap-3">
          <Input value={path} onChange={(e) => setPath(e.target.value)} placeholder="Enter directory path..." className="flex-1" />
          <Button
            onClick={async () => {
              try {
                await ingestPath({ paths: [path], max_chunk_tokens: 512, overlap: 64 });
                alert('✅ Ingestion started/completed');
              } catch (error) {
                alert(`❌ Error: ${error instanceof Error ? error.message : 'Ingestion failed'}`);
              }
            }}
            disabled={isPending}
          >
            {isPending ? '🔄 Processing...' : '🚀 Build Index'}
          </Button>
        </div>
        <p className="text-sm text-black bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-purple-200">
          💡 Provide a directory path containing .md/.pdf/.html files to build the search index.
        </p>
      </div>

      {/* Ingest Status */}
      <div className="glass rounded-xl p-6 shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-black">📊 Ingest Status</h2>
          <button onClick={() => refetchStatus()} className="px-3 py-1 text-sm rounded-lg bg-gradient-to-r from-gray-100 to-gray-200 text-black hover:from-gray-200 hover:to-gray-300 transition-all duration-200">
            🔄 Refresh
          </button>
        </div>
        {status ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border border-purple-200">
                <div className="text-sm text-gray-600">Total Documents</div>
                <div className="text-2xl font-bold text-black">{status.total_documents}</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
                <div className="text-sm text-gray-600">Total Chunks</div>
                <div className="text-2xl font-bold text-black">{status.total_chunks}</div>
              </div>
            </div>
            {status.documents && status.documents.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-black mb-2">Recent Documents ({status.documents.length}):</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {status.documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-white to-blue-50 border border-purple-200 rounded-lg hover:shadow-md transition-all duration-200"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-black truncate">{doc.title}</div>
                        <div className="text-xs text-gray-500 truncate">{doc.source}</div>
                        <div className="text-xs text-gray-400 mt-1">
                          {doc.chunk_count} chunks • {doc.created_at ? new Date(doc.created_at).toLocaleString() : 'Unknown date'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-sm text-gray-500">Loading status...</div>
        )}
      </div>
    </main>
  );
}


