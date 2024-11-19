import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Subject } from 'rxjs';
import Web3 from 'web3';
import { Product, Web3EnabledWindow } from '../models';

import { MessageService } from 'primeng/api';
import { tokenInterface } from 'src/assets/json-interfaces/m0leCoin';
import { bankInterface } from 'src/assets/json-interfaces/m0leBank';
import { shopInterface } from 'src/assets/json-interfaces/m0leShop';

@Injectable({
  providedIn: 'root'
})
export class Web3Service {
  private window: Web3EnabledWindow;
  private accounts: any[] | undefined;
  web3: Web3 | undefined;
  private tokenContract: any;
  private bankContract: any;
  private shopContract: any;

  private linkStatusSource = new Subject<boolean>();
  linkStatus = this.linkStatusSource.asObservable();

  constructor(
    private messageService: MessageService
  ) {
    this.window = window;
    if (!this.window.ethereum) {
      this.messageService.add({severity: 'error', summary: 'MetaMask not installed.'});
      return;
    } else {
      this.window.ethereum.on('disconnect', () => {
        this.linkStatusSource.next(false);
      });
    }
  }

  async connectAccount() {
    try {
      // Unlock MetaMask and connect user accounts
      await this.window.ethereum.request({ method: 'eth_requestAccounts' });
    } catch (err) {
      // something on error
      this.messageService.add({severity: 'error', summary: 'Provider linking error.'});
      return [];
    }
    this.messageService.add({severity: 'success', summary: 'Provider linked.'});
    // Wrap provider with web3 convenience library
    this.web3 = new Web3(this.window.ethereum);
    this.tokenContract = new this.web3.eth.Contract(tokenInterface, environment.tokenContractAddress);
    this.bankContract = new this.web3.eth.Contract(bankInterface, environment.bankContractAddress);
    this.shopContract = new this.web3.eth.Contract(shopInterface, environment.shopContractAddress)
    this.linkStatusSource.next(true);
    this.accounts = await this.web3.eth.getAccounts(); 
    return this.accounts;
  }

  async sign(data: string, address: string) {
    try {
      if (this.web3) {
        return await this.web3.eth.personal.sign(data, address, '');
      }  
      this.messageService.add({severity: 'error', summary: 'Sign failed. Web3 not initialized'});
      return '';
    } catch (err) {
      this.messageService.add({severity: 'error', summary: 'Sign failed.'});
      return '';
    }
  }

  async getUserBalance() {
    if (this.tokenContract) {
      try {
        const balance = await this.tokenContract.methods.getBalance().call({from: this.web3?.eth.defaultAccount});
        return balance;
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Check balance failed.'});
        return 0;
      }
    }
  }

  async transferTokens(dest: string, amount: number) {
    if (this.tokenContract) {
      try {
        await this.tokenContract.methods.transfer(dest, amount).send({from: this.web3?.eth.defaultAccount});
        this.messageService.add({severity: 'success', summary: 'Transfer complete.'});
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Transfer failed.'});
      }
    }
  }

  async checkBankRegistration() {
    if (this.bankContract) {
      try {
        const res = await this.bankContract.methods.isRegistered().call({from: this.web3?.eth.defaultAccount});
        return res;
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Bank account check failed.'});
        return false;
      }
    }
  }

  async openBankAccount(mhash: string, v: number, r: string, s: string) {
    if (this.bankContract) {
      try {
        await this.bankContract.methods.openAccount(v,r,s,mhash).send({from: this.web3?.eth.defaultAccount});
        this.messageService.add({severity: 'success', summary: 'Account opened.'});
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Account creation failed.'});
      }
    }
  }

  async getUserBankBalance() {
    if (this.bankContract) {
      try {
        const bal = await this.bankContract.methods.getBalance().call({from: this.web3?.eth.defaultAccount});
        return bal;
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Check bank balance failed.'});
        return 0;
      }
    }
  }

  async bankDeposit(amount: number) {
    if (this.bankContract) {
      try {
        await this.bankContract.methods.deposit(amount).send({from: this.web3?.eth.defaultAccount});
        this.messageService.add({severity: 'success', summary: 'Deposited.'});
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Deposit failed.'});
      }
    }
  }

  async bankWithdraw() {
    if (this.bankContract) {
      try {
        await this.bankContract.methods.withdraw().send({from: this.web3?.eth.defaultAccount});
        this.messageService.add({severity: 'success', summary: 'Withdrawn.'});
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Withdrawal failed.'});
      }
    }
  }

  async getProductPrice(productId: number) {
    if (this.shopContract) {
      try {
        const price = await this.shopContract.methods.getPriceById(productId).call({from: this.web3?.eth.defaultAccount});
        return price;
      } catch (err) {
        return -1;
      }
    }
  }

  async shopBuyProduct(productId: number) {
    if (this.shopContract) {
      try {
        await this.shopContract.methods.buy(productId).send({from: this.web3?.eth.defaultAccount});
      } catch (err){
        this.messageService.add({severity: 'error', summary: 'Buy of product id-' + productId.toString() + ' failed.'});
      }
    }
  }

  async shopPutOnSale(product: Product) {
    if (this.shopContract) {
      try {
        await this.shopContract.methods.putOnSale(product.id, product.price).send({from: this.web3?.eth.defaultAccount});
      } catch (err) {
        this.messageService.add({severity: 'error', summary: 'Put on sale of product -' + product.id.toString() + ' failed.'});
        throw new Error();
      }
    }
  }
}
