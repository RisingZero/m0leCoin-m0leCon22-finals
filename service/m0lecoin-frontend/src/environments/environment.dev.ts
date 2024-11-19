// This file can be replaced during build by using the `fileReplacements` array.
// `ng build` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
    production: false,
    baseUrl: `${location.protocol}//${location.hostname}:8000/api`,
    tokenContractAddress: '0x3d554d562e4D4a7E7E88674FE64846200737ed21',
    bankContractAddress: '0xCC715Bb9EC9fa3F35B40528089B980C7c4c8BDDf',
    shopContractAddress: '0xE3Ed7978A2EFfD0A932cE0599eAd89fBECa86fA7'
  };
  
  /*
   * For easier debugging in development mode, you can import the following file
   * to ignore zone related error stack frames such as `zone.run`, `zoneDelegate.invokeTask`.
   *
   * This import should be commented out in production mode because it will have a negative impact
   * on performance if an error is thrown.
   */
  // import 'zone.js/plugins/zone-error';  // Included with Angular CLI.
  