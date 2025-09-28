import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, File, CheckCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { formatFileSize, formatDate } from '@/utils/text';
import { apiService } from '@/services/api';
import toast from 'react-hot-toast';

interface UploadFormData {
  path: string;
  file: FileList;
}

interface UploadResult {
  fileName: string;
  doc_id: string;
  chunks: number;
  timestamp: Date;
}

export const UploadTab: React.FC = () => {
  const [recentUploads, setRecentUploads] = useState<UploadResult[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<UploadFormData>({
    defaultValues: {
      path: 'kb/',
    },
  });

  const selectedFiles = watch('file');

  const uploadMutation = useMutation({
    mutationFn: ({ file, path }: { file: File; path: string }) =>
      apiService.uploadFile(file, path),
    onSuccess: (data, variables) => {
      const result: UploadResult = {
        fileName: variables.file.name,
        doc_id: data.doc_id,
        chunks: data.chunks,
        timestamp: new Date(),
      };
      
      setRecentUploads(prev => [result, ...prev.slice(0, 4)]);
      toast.success(`File uploaded successfully! Generated ${data.chunks} chunks.`);
      reset({ path: 'kb/' });
      
      // Invalidate docs query to refresh the list
      queryClient.invalidateQueries(['admin-docs']);
    },
    onError: (error) => {
      toast.error(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    },
  });

  const onSubmit = (data: UploadFormData) => {
    if (!data.file || data.file.length === 0) return;
    
    const file = data.file[0];
    uploadMutation.mutate({ file, path: data.path });
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      // Create a FileList-like object for react-hook-form
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(files[0]);
      setValue('file', dataTransfer.files);
    }
  };

  return (
    <div className="space-y-8">
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Upload Documents
        </h2>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            {...register('path', { required: 'Path is required' })}
            label="Path"
            placeholder="kb/documents/..."
            error={errors.path?.message}
            helperText="Specify where to store the document in your knowledge base"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              File
            </label>
            <div
              className={`relative border-2 border-dashed rounded-lg p-6 transition-colors ${
                dragActive
                  ? 'border-primary-400 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="mt-4">
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer text-primary-600 hover:text-primary-500 font-medium"
                  >
                    Choose a file
                  </label>
                  <span className="text-gray-500"> or drag and drop</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  PDF, TXT, MD, DOCX up to 50MB
                </p>
              </div>
              <input
                {...register('file', { required: 'File is required' })}
                id="file-upload"
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                accept=".pdf,.txt,.md,.docx"
              />
            </div>
            {errors.file && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                {errors.file.message}
              </p>
            )}
          </div>

          {selectedFiles && selectedFiles.length > 0 && (
            <Card className="bg-gray-50 dark:bg-gray-900">
              <div className="flex items-center space-x-3">
                <File className="w-5 h-5 text-gray-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {selectedFiles[0].name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {formatFileSize(selectedFiles[0].size)}
                  </p>
                </div>
              </div>
            </Card>
          )}

          <Button
            type="submit"
            loading={uploadMutation.isLoading}
            disabled={!selectedFiles || selectedFiles.length === 0}
            className="w-full"
          >
            Upload Document
          </Button>
        </form>
      </Card>

      {recentUploads.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Uploads
          </h3>
          <div className="space-y-3">
            {recentUploads.map((upload, index) => (
              <div
                key={`${upload.doc_id}-${index}`}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {upload.fileName}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatDate(upload.timestamp.toISOString())}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="success" size="sm">
                    {upload.chunks} chunks
                  </Badge>
                  <code className="text-xs text-gray-500 dark:text-gray-400">
                    {upload.doc_id}
                  </code>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};
