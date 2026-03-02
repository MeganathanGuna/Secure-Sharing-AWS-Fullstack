import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { UploadComponent } from './pages/upload/upload.component';
import { AuthorizeComponent } from './pages/authorize/authorize.component';
import { AccessCheckComponent } from './pages/access-check/access-check.component';
import { DownloadComponent } from './pages/download/download.component';
import { BlockchainComponent } from './pages/blockchain/blockchain.component';

const routes: Routes = [
  { path: '', redirectTo: 'upload', pathMatch: 'full' },
  { path: 'upload', component: UploadComponent },
  { path: 'authorize', component: AuthorizeComponent },
  { path: 'access-check', component: AccessCheckComponent },
  { path: 'download', component: DownloadComponent },
  { path: 'blockchain', component: BlockchainComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
