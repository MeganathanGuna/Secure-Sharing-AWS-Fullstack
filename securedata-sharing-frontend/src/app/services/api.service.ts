// src/app/services/api.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private BASE_URL = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  uploadFile(formData: FormData) {
    return this.http.post(
      `${this.BASE_URL}/upload`,
      formData
    );
  }

  authorize(data: any) {
    return this.http.post(`${this.BASE_URL}/authorize`, data);
  }

  accessCheck(data: any) {
    return this.http.post(`${this.BASE_URL}/access-check`, data);
  }

  download(data: any) {
    return this.http.post(`${this.BASE_URL}/download`, data, { responseType: 'blob' });
  }

  getChain() {
    return this.http.get(`${this.BASE_URL}/chain`);
  }
}