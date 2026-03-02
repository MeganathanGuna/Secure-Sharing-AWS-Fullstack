// src/app/pages/upload/upload.component.ts
import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html'
})
export class UploadComponent {

  ownerId = '';
  selectedFile!: File;
  fileHash = '';

  constructor(private api: ApiService) {}

  onFileSelect(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
  const formData = new FormData();
  formData.append('file', this.selectedFile);
  formData.append('owner_id', this.ownerId);

  this.api.uploadFile(formData).subscribe({
    next: (res: any) => {
      this.fileHash = res.file_hash;
      alert('Upload successful');
    },
    error: (err) => {
      console.error(err);
      alert('Upload failed');
    }
  });
}

}