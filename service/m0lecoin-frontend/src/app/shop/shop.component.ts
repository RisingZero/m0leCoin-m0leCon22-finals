import { Component, OnInit } from '@angular/core';
import { ApiService, AuthService, Web3Service } from '../services';

import { MessageService } from 'primeng/api';

import { Product, Gadget, GenericResponse } from '../models';

import * as crypto from 'crypto';

@Component({
  selector: 'app-shop',
  templateUrl: './shop.component.html',
  styleUrls: ['./shop.component.scss']
})
export class ShopComponent implements OnInit {

  mode: 'buy' | 'sell' | 'gadget' = 'buy';

  userBalance = 0;
  userAddress = '';

  // Sell mode state variables
  productTitle = '';
  productContent = '';
  productPrice = 0;
  price = 0;

  // Buy mode state variables
  products: Product[] = [];
  selectedProductId = 0;
  selectedProductTitle = '';
  selectedProductContent = '';
  selectedProductSeller = '';
  showSelectedProduct = false;

  // Gadget mode state variables
  gadgets: Gadget[] = [];
  gadgetContent = '';
  receiverMailbox = '';
  gadgetKey = '';

  constructor(
    private web3Service: Web3Service,
    private auth: AuthService,
    private api: ApiService,
    private messageService: MessageService
  ) { }

  ngOnInit(): void {
    this.getUserBalance();
    this.userAddress = this.auth.getUserAddress();
    if (this.mode === 'buy') {
      this.fetchProducts();
    } else if (this.mode === 'gadget') {
      this.fetchGadgets();
    }
  }

  getUserBalance() {
    this.web3Service.getUserBalance()
      .then(b => this.userBalance = b);
  }

  fetchProducts() {
    this.api.getShopProducts()
      .then(
        async (res: Product[]) => {
          this.products = res;
          for (let i = 0; i < this.products.length; i++) {
            this.products[i].price = parseInt(await this.web3Service.getProductPrice(this.products[i].id));
          }
        }
      )
      .catch(err => {
        this.messageService.add({severity: 'error', summary: 'Product fetch failed.', detail: err});
      });
  }

  clickProduct(productId: number, seller: string) {
    if (seller === this.userAddress) {
      this.deleteProduct(productId);
    } else {
      this.buyProduct(productId);
    }
  }

  buyProduct(productId: number) {
    this.web3Service.shopBuyProduct(productId)
      .then(() => this.getUserBalance());
  }

  deleteProduct(productId: number) {
    this.api.revertSellShopProduct(productId)
    .then((res: GenericResponse) => {
      if (!res.success) {
        this.messageService.add({severity: 'error', summary: 'Failed reverting id-' + productId.toString() +'.'});
      } else {
        this.fetchProducts();
      }
    });
  }

  seeProduct(productId: number) {
    this.api.getShopProductContent(productId)
      .then((p: Product) => {
        this.selectedProductId = p.id;
        this.selectedProductTitle = p.title;
        this.selectedProductContent =  p.content;
        this.selectedProductSeller = p.seller;
        this.showSelectedProduct = true;
      })
      .catch(err => this.messageService.add({severity: 'error', summary: 'Product open failed.', detail: err}))
  }

  sellProduct() {
    const product: Product = {
      id: 0,
      title: this.productTitle,
      content: this.productContent,
      seller: '',
      price: this.productPrice
    }
    this.api.sellShopProduct(product)
      .then((p: Product) => {
        if (p.id == null) {
          this.messageService.add({severity: 'error', summary: 'Product sell failed.', detail: product.content});
          return;
        }
        p.price = product.price;
        this.web3Service.shopPutOnSale(p)
        .then(() => {
          this.messageService.add({severity: 'success', summary: 'Product put on sale with id ' + p.id.toString() +'.'});
          this.clearNewProduct();
        })
        .catch(() => {
          this.messageService.add({severity: 'error', summary: 'Put on sale error id-' + p.id.toString() +'.'});
          this.deleteProduct(p.id);
        });
      })
  }

  clearNewProduct() {
    this.productTitle = '';
    this.productContent = '';
    this.productPrice = 0;
    this.gadgetContent = '';
    this.receiverMailbox = '';
  }

  fetchGadgets() {
    this.api.getGadgets()
      .then(
        async (res: Gadget[]) => {
          this.gadgets = res;
        }
      )
      .catch(err => {
        this.messageService.add({severity: 'error', summary: 'Gadget fetch failed.', detail: err});
      });
  }

  publishGadget() {
    const gadget: Gadget = {
      id: 0,
      content: this.gadgetContent,
      seller: ''
    }
    this.api.publishGadget(gadget)
    .then((g: Gadget) => {
      if (g.id == null) {
        this.messageService.add({severity: 'error', summary: 'Gadget publish failed.', detail: g.content});
        return;
      }
      this.messageService.add({severity: 'success', summary: 'Gadget published with id ' + g.id.toString() +'.'});
      this.clearNewProduct();
      this.fetchGadgets();
    })
  }

  sendGadget(gadgetId: number) {
    let hmac = crypto
    .createHmac('sha256', this.gadgetKey)
    .update(this.receiverMailbox)
    .digest('hex') 
    this.api.sendGadgetToMailbox(this.receiverMailbox, hmac, gadgetId)
    .then((res: GenericResponse) => {
      if (!res.success) {
        this.messageService.add({severity: 'error', summary: 'Failed sending gadget id-' + gadgetId.toString() +'.'});
      } else {
        this.messageService.add({severity: 'success', summary: 'Gadget sent to specified mailbox.'});
      }
    });
  }

  updateGadgetKey() {
    this.api.updateGagdetKey(this.gadgetKey)
    .then((res: GenericResponse) => {
      if (!res.success) {
        this.messageService.add({severity: 'error', summary: 'Failed updating gadget management key .'});
      } else {
        this.messageService.add({severity: 'success', summary: 'Profile gadget key updated.'});
        this.fetchGadgets();
      }
    });
  }

  deleteGadget(gadgetId: number) {
    this.api.deleteGadget(gadgetId)
      .then((res: GenericResponse) => {
        if (!res.success) {
          this.messageService.add({severity: 'error', summary: 'Failed deleted gadget id-' + gadgetId.toString() +'.'});
        } else {
          this.messageService.add({severity: 'success', summary: 'Gadget deleted.'});
          this.fetchGadgets();
        }
      });
  }

  changeMode(_mode: 'buy' | 'sell' | 'gadget') {
    this.mode = _mode;

    if (_mode === 'buy') {
      this.fetchProducts();
      this.getUserBalance();
    }

    if (_mode === 'gadget') {
      this.clearNewProduct();
      this.fetchGadgets();
    }

    if (_mode ==='sell') {
      this.clearNewProduct();
      this.getUserBalance();
    }
  }

}
