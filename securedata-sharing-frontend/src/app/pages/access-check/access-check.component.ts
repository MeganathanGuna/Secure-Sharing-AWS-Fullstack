// src/app/pages/access-check/access-check.component.ts
import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-access-check',
  templateUrl: './access-check.component.html',
  styleUrls: ['./access-check.component.css']
})
export class AccessCheckComponent {
  fileHash = '';
  userId = '';
  result = '';

  constructor(private api: ApiService) {}

  check() {
    this.api.accessCheck({
      file_hash: this.fileHash,
      user_id: this.userId
    }).subscribe((res: any) => {
      this.result = res.access === true
        ? '✅ ACCESS GRANTED'
        : '❌ ACCESS DENIED';
    });
  }
}