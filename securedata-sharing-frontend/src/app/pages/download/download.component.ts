// src/app/pages/download/download.component.ts
import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-download',
  templateUrl: './download.component.html',
  styleUrls: ['./download.component.css']
})
export class DownloadComponent {
  fileHash = '';
  userId = '';

  constructor(private api: ApiService) {}

  download() {
    this.api.download({
      file_hash: this.fileHash,
      user_id: this.userId
    }).subscribe({
      next: (blob: Blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `downloaded-${this.fileHash.slice(0, 8)}`;  // Fallback, backend handles real name
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        if (err.status === 403) {
          alert('Access denied');
        } else {
          alert('Download failed');
        }
      }
    });
  }
}