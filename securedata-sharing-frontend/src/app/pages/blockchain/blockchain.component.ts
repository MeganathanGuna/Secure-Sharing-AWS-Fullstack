// src/app/pages/blockchain/blockchain.component.ts
import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-blockchain',
  templateUrl: './blockchain.component.html',
  styleUrls: ['./blockchain.component.css']
})
export class BlockchainComponent implements OnInit{
  chain: any[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getChain().subscribe((res: any) => {
      this.chain = res.chain;
    });
  }
}