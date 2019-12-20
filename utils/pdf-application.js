var webConfig = require("../config/web.js");
const env = process.env.NODE_ENV || 'development';
const config = require(__dirname + '/../config/config.json')[env];
const Hubspot = require('hubspot')
let fs = require('fs');
let ejs = require('ejs');
var webshot = require('webshot');
let request = require('request');

module.exports = {

  getFileName: function(uuid, hubspotCompanyId, extension){
    return 'trucking-insurance-application-'+((hubspotCompanyId)?hubspotCompanyId:uuid)+((extension)?'.pdf':'');
  },
  get: async function(uuid, hubspotCompanyId, companyModel) {
    return new Promise(async (resolve, reject) => {

      try{

        let html = await this.getHTML(uuid, companyModel);
        let pdfLocation = webConfig.rootDir+'/public/trucking-insurance-application/'+this.getFileName(uuid, hubspotCompanyId, true);

        let pdfOptions = {
          "paperSize": {
              "format": "A2", 
              "orientation": "portrait", 
              "border": "0.15cm"
          },
          siteType:'html'
        };

        if (fs.existsSync(pdfLocation)) {
            fs.unlinkSync(pdfLocation)
        }
        
        webshot(html, pdfLocation, pdfOptions, function(err) {
            resolve(pdfLocation);
        });
  
      }catch(e){
        console.log(e);
        reject(e)
      }


    })
  },

  uploadToHubspot: async function(uuid, hubspotCompanyId, companyModel) {
    return new Promise(async (resolve, reject) => {

      const hubspot = new Hubspot({ 
        apiKey: config.hapikey,
        checkLimit: false // (Optional) Specify whether or not to check the API limit on each call. Default: true 
      })

      let previousFileId = '';
      let engagements = await hubspot.engagements.getAssociated('COMPANY', hubspotCompanyId, {}).catch(err => {
        console.log('previous file ready error', err);
      })

      //console.log('engagements of '+hubspotCompanyId, engagements);
      // console.log("engagment",engagements)
      // console.log("engagements.results",engagements.results)
      if(engagements && engagements.results && Array.isArray(engagements.results) && engagements.results.length){
       // console.log('!! inside if !!');
        for(let c = 0; c < engagements.results.length > c; c++){
         // console.log('S1: ', c);
          if(Array.isArray(engagements.results[c].attachments) && engagements.results[c].attachments.length){
              for(let cc = 0; cc < engagements.results[c].attachments.length > cc; cc++){
                  //console.log('S2: ', cc);
                  try{
                    let tmp = await hubspot.files.getOne(engagements.results[c].attachments[cc].id);
                    if(tmp.title.indexOf(this.getFileName(uuid, hubspotCompanyId, false)) > -1)previousFileId = tmp.id;

                    //console.log('name 1', tmp.title);
                    //console.log('name 2', this.getFileName(uuid, hubspotCompanyId, false));
                    //console.log('index of', tmp.title.indexOf(this.getFileName(uuid, hubspotCompanyId, false)));
                  }catch(e){ 
                   //console.log('getFileName',e);
                  }
              }
          }
    
        }
      }

      //console.log(previousFileId);
      /*if(!previousFileId){
        console.log('previousFileId is empty', previousFileId);
        reject('previousFileId is empty');
        return
      }*/

      let pdfLocation = await this.get(uuid, hubspotCompanyId, companyModel);

      if (!fs.existsSync(pdfLocation)) {
        console.log('pdfLocation', pdfLocation);
        reject('pdf file nof found');
        return
      }

      let formData = {
          'file': fs.createReadStream(pdfLocation),
          'jsonUpload': JSON.stringify({})
      };
      let uploadOptions = {
          "url": "http://api.hubapi.com/filemanager/api/v2/files/"+previousFileId+"?hapikey="+config.hapikey,
          "method": "POST",
          "headers": {},
          "formData": formData
      }
      request(uploadOptions, function(err, resp, body) {
          if (err) {
              console.log(err);
              reject(err);
          } else {

              if(!previousFileId){
                let obj = JSON.parse(body);

                const properties = {
                  "engagement": {
                      "active": true,
                      "ownerId": null,
                      "type": "NOTE",
                      "timestamp": Date.now()
                  },
                  "associations": {
                      "contactIds": [ ],
                      "companyIds": [ hubspotCompanyId ],
                      "dealIds": [ ],
                      "ownerIds": [ ]
                  },
                  "attachments": [
                      {
                          "id": obj.objects[0].id
                      }
                  ],
                  "metadata": {
                      "body": "note body"
                  }
                }
              
                hubspot.engagements.create(properties).then(engagement => {
                    console.log(engagement);
                    resolve('ok')
                }).catch(err => {
                    reject(err)
                })

              }else{
                console.log(body);
                resolve('ok')
              }

              


          }
      });


    })
  },
  getHTML: async function(uuid, companyModel) {
    return new Promise(async (resolve, reject) => {

      let contents = fs.readFileSync(webConfig.rootDir+'/views/trucking_insurance_application_pdf/index.ejs').toString();
      let logo = fs.readFileSync(webConfig.rootDir+'/views/trucking_insurance_application_pdf/mini_logo.png');
      
      let logo64 = Buffer(logo).toString('base64');
      
      let ejsOptions = {
        logo: 'data:image/jpg;base64,'+logo64,
        signSignature: '',
        company_name: "",
        dba_name: "",
        phone_number: "",
        mailing_address: "",
        mailing_city: "",
        mailing_state: "",
        mailing_zip: "",
        garaging_address: "",
        garaging_city: "",
        garaging_state: "",
        garaging_zip: "",
        policy_term_from: "",
        policy_term_to: "",
        dot_number: "",
        mc_number: "",
        email_address: "",
        business_start_date: "",
        cargoHauled: [],
        cargoHauledLeft: 5,
        owners: [],
        ownersLeft: 3,
        drivers: [],
        driversLeft: 5,
        vehiclesTrailers: [],
        vehiclesTrailersLeft: 10,
        accidents: "",
        eldProvider: "",
        comments: "",
        radiusOfTravel: 0,
        currentCarrier: ""
      }

      let profile = await companyModel.findByUUID(uuid);
      if(!profile){
        
        reject('the company not found by uuid')
        return
      }
      const fullProfile = profile; 

      ejsOptions.signSignature = fullProfile.signSignature.imageSign;

      if(fullProfile.currentEldProvider){
        try {
	      	if (!Array.isArray(fullProfile.currentEldProvider)) {
	        	ejsOptions.eldProvider = JSON.parse(fullProfile.currentEldProvider).join(', ');
	    	} else {
	    		ejsOptions.eldProvider = fullProfile.currentEldProvider.join(', ');
	    	}
        } catch (e) {}
      }

      ejsOptions.mc_number = fullProfile.mcNumber;
      ejsOptions.email_address = fullProfile.emailAddress;
      ejsOptions.dba_name = fullProfile.dba;
      ejsOptions.phone_number = fullProfile.phoneNumber;
      ejsOptions.company_name = fullProfile.name;
      ejsOptions.dot_number = fullProfile.dotNumber;
      ejsOptions.currentCarrier = fullProfile.currentCarrier;
      
      if(fullProfile.mailingAddress){
        try {
        	let mailing_address = fullProfile.mailingAddress;
	      	if (fullProfile.mailingAddress.constructor !== Object) {
	        	mailing_address = JSON.parse(fullProfile.mailingAddress);
	    	}
          ejsOptions.mailing_address = mailing_address.address;
          ejsOptions.mailing_zip = mailing_address.zip;
          ejsOptions.mailing_city = mailing_address.city;
          ejsOptions.mailing_state = mailing_address.state;
        } catch (e) {}
      }

      if(fullProfile.garagingAddress){
        try {
        	let garaging_address = fullProfile.garagingAddress;
	      	if (fullProfile.garagingAddress.constructor !== Object) {
	        	garaging_address = JSON.parse(fullProfile.garagingAddress);
	    	}
          	ejsOptions.garaging_address = garaging_address.address;
          	ejsOptions.garaging_zip = garaging_address.zip;
          	ejsOptions.garaging_city = garaging_address.city;
          	ejsOptions.garaging_state = garaging_address.state;
        } catch (e) {}
      }

      if(fullProfile.cargoHauled){
        try {
          let cargoHauled = fullProfile.cargoHauled;
          if (fullProfile.vehicleInformationList.constructor !== Object) {
          	cargoHauled = JSON.parse(fullProfile.cargoHauled);
          }
          Object.keys(cargoHauled).forEach(groupName => {
              let str = groupName+": "+ cargoHauled[groupName].join(', ');
              ejsOptions.cargoHauled.push(str);
          });
        } catch (e) {}
      }

      	if (fullProfile.driverInformationList) {
      		ejsOptions.drivers	= fullProfile.driverInformationList;
      		if (!Array.isArray(fullProfile.driverInformationList)) {
     	 		ejsOptions.drivers = JSON.parse(fullProfile.driverInformationList);
      		}
 	 	} else {
 	 		ejsOptions.drivers = [];
 	 	}

 	 	if (fullProfile.ownerInformationList) {
 	 		ejsOptions.owners	= fullProfile.ownerInformationList;
      		if (!Array.isArray(fullProfile.ownerInformationList)) {
     	 		ejsOptions.owners = JSON.parse(fullProfile.ownerInformationList);
      		}
 	 	} else {
 	 		ejsOptions.owners = [];
 	 	}

      ejsOptions.comments = fullProfile.comments;

      if(ejsOptions.drivers.length < 3) {
        for (var i = 0; i < 3; i++) {
          ejsOptions.drivers.push({});
        }
      }

      if(ejsOptions.owners.length < 3) {
        for (var i = 0; i < 3; i++) {
          ejsOptions.owners.push({});
        }
      }
      
      if (fullProfile.vehicleInformationList) {
      	let vehileList = fullProfile.vehicleInformationList;
      	if (fullProfile.vehicleInformationList.constructor !== Object) {
        	vehileList = JSON.parse(fullProfile.vehicleInformationList);
    	}
        try {
          if(vehileList.vehicle.length){
             vehileList.vehicle.map(vehicle => {
                ejsOptions.radiusOfTravel += parseInt(vehicle.radiusOfTravelVehicle);
                ejsOptions.vehiclesTrailers.push(vehicle);
             })
          }
          ejsOptions.radiusOfTravel /= vehileList.vehicle.length;
        } catch (e) {}
        
        if(vehileList.trailer.length){
          vehileList.trailer.map(trailer => {
            ejsOptions.radiusOfTravel += parseInt(trailer.radiusOfTravelVehicle);
            ejsOptions.vehiclesTrailers.push(trailer);
          })
        	ejsOptions.radiusOfTravel /= vehileList.trailer.length;
        }
      }

      if(ejsOptions.vehiclesTrailers.length < 10) {
        for (var i = 0; i < 10; i++) {
          ejsOptions.vehiclesTrailers.push({});
        }
      }
     // console.log('ejsOpttions:'+ JSON.parse(ejsOptions));
      html = ejs.render(contents, ejsOptions);

      resolve(html);
    });
  }
};