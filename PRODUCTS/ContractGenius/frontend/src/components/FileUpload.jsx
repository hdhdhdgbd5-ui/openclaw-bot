import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, AlertCircle } from 'lucide-react'

const FileUpload = ({ onFileSelect, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [error, setError] = useState(null)

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null)
    
    if (rejectedFiles.length > 0) {
      setError('Please upload a PDF, DOCX, or TXT file (max 50MB)')
      return
    }
    
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      setSelectedFile(file)
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: false,
    disabled: isLoading,
  })

  const clearFile = () => {
    setSelectedFile(null)
    setError(null)
    onFileSelect(null)
  }

  const getFileIcon = () => {
    if (!selectedFile) return <Upload className="h-12 w-12 text-primary-500" />
    
    const ext = selectedFile.name.split('.').pop().toLowerCase()
    
    switch (ext) {
      case 'pdf':
        return (
          <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center">
            <span className="text-red-600 font-bold text-sm">PDF</span>
          </div>
        )
      case 'docx':
        return (
          <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span className="text-blue-600 font-bold text-xs">DOCX</span>
          </div>
        )
      case 'txt':
        return (
          <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
            <span className="text-gray-600 font-bold text-sm">TXT</span>
          </div>
        )
      default:
        return <File className="h-12 w-12 text-gray-400" />
    }
  }

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
          ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          ${selectedFile ? 'bg-green-50 border-green-300' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {getFileIcon()}
          
          {selectedFile ? (
            <div className="flex items-center space-x-2">
              <span className="font-medium text-gray-900">{selectedFile.name}</span>
              {!isLoading && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    clearFile()
                  }}
                  className="p-1 hover:bg-gray-200 rounded transition-colors"
                >
                  <X className="h-4 w-4 text-gray-500" />
                </button>
              )}
            </div>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-700">
                {isDragActive ? 'Drop your contract here' : 'Drag & drop your contract'}
              </p>
              <p className="text-sm text-gray-500">
                or click to browse (PDF, DOCX, TXT up to 50MB)
              </p>
            </>
          )}
        </div>
      </div>
      
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}
    </div>
  )
}

export default FileUpload