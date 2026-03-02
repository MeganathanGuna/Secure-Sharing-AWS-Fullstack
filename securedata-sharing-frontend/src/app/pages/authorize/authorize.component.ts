// src/app/pages/authorize/authorize.component.ts
import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-authorize',
  templateUrl: './authorize.component.html',
  styleUrls: ['./authorize.component.css']
})
export class AuthorizeComponent {
  fileHash = '';
  ownerId = '';
  userId = '';

  constructor(private api: ApiService) {}

  authorize() {
    this.api.authorize({
      file_hash: this.fileHash,
      owner_id: this.ownerId,
      new_user_id: this.userId
    }).subscribe(() => alert('Authorization recorded'));
  }
}