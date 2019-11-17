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

        //console.log(pdfLocation);
        //resolve(pdfLocation);
        
        
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
      let logo = fs.readFileSync(webConfig.rootDir+'/views/trucking_insurance_application_pdf/logo.jpg');
      
      let logo64 = Buffer(logo).toString('base64');
      
      let ejsOptions = {
        logo: 'data:image/jpg;base64,'+logo64,
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
      }

      
      let profile = await companyModel.findByUUID(uuid);
      if(!profile){
        
        reject('the company not found by uuid')
        return
      }
      console.log('getHTML:'+ JSON.stringify(profile));
      let fullProfile = companyModel.renderAllByType(profile);

      console.log('FullProfile:'+ JSON.stringify(fullProfile));
        if(fullProfile.eldProvider && Array.isArray(fullProfile.eldProvider.eldProvider)){
          ejsOptions.eldProvider = fullProfile.eldProvider.eldProvider.join(', ');
        }

        if(fullProfile.businessStructure){
          if(fullProfile.businessStructure["MC"]){
              ejsOptions.mc_number = fullProfile.businessStructure["MC"];
          }
        }
        // console.log('bsa:'+ JSON.stringify(fullProfile.businessStructureRaw));
        // console.log('DBA Name:'+JSON.stringify(fullProfile.businessStructureRaw["Legal Name"]));
        if(fullProfile.businessStructureRaw){

            let accidents = 0;
            if(fullProfile.businessStructureRaw["Crashes"] && fullProfile.businessStructureRaw["Crashes"]["US"] && fullProfile.businessStructureRaw["Crashes"]["US"]["Crashes"]){
              accidents += parseInt(fullProfile.businessStructureRaw["Crashes"]["US"]["Crashes"]["Total"], 10);
            }
  
            if(fullProfile.businessStructureRaw["Crashes"] && fullProfile.businessStructureRaw["Crashes"]["Canada"] && fullProfile.businessStructureRaw["Crashes"]["Canada"]["Crashes"]){
              accidents += parseInt(fullProfile.businessStructureRaw["Crashes"]["Canada"]["Crashes"]["Total"], 10);
            }
  
            if(accidents)ejsOptions.accidents = 'YES: '+accidents;
            console.log('name:'+fullProfile.businessStructureRaw["DBA Name"]);
            if(fullProfile.businessStructureRaw["Email Address"])ejsOptions.email_address = fullProfile.businessStructureRaw["Email Address"];
            if(fullProfile.businessStructureRaw["DBA Name"])ejsOptions.dba_name = fullProfile.businessStructureRaw["DBA Name"];
            if(fullProfile.businessStructureRaw["Phone"])ejsOptions.phone_number = fullProfile.businessStructureRaw["Phone"];
            if(fullProfile.businessStructureRaw["Legal Name"])ejsOptions.company_name = fullProfile.businessStructureRaw["LegalName"];
            if(fullProfile.businessStructureRaw["USDOT Number"])ejsOptions.dot_number = fullProfile.businessStructureRaw["USDOT Number"];
  
            if(fullProfile.businessStructureRaw["Mailing Address"]){
              ejsOptions = companyModel.parseAndAssignAddress(fullProfile.businessStructureRaw["Mailing Address"], ejsOptions, 'mailing_');
            }
  
            if(fullProfile.businessStructureRaw["Physical Address"]){
              ejsOptions = companyModel.parseAndAssignAddress(fullProfile.businessStructureRaw["Physical Address"], ejsOptions, 'garaging_');
            }
        }

        if(fullProfile.cargoHauled && fullProfile.cargoHauled.haulType){

          Object.keys(fullProfile.cargoHauled.haulType).forEach(async groupName => {
              let str = groupName+": "+fullProfile.cargoHauled.haulType[groupName].join(', ');
              ejsOptions.cargoHauled.push(str);
          });
        }

        ejsOptions.drivers = (fullProfile.drivers)?fullProfile.drivers:[];
        ejsOptions.owners = (fullProfile.owners)?fullProfile.owners:{owners: []};

        //{"question1": 
        // if(fullProfile.questions && (fullProfile.questions.question1 || fullProfile.questions.question2)){
        //   ejsOptions.comments = fullProfile.questions.question1+"; "+fullProfile.questions.question2;
        // }

        if(fullProfile.questions && fullProfile.questions.question1){
          ejsOptions.comments = fullProfile.questions.question1+"."
        }
        


        //start tmp
        if(ejsOptions.drivers.length < 3)ejsOptions.drivers.push({});
        if(ejsOptions.drivers.length < 3)ejsOptions.drivers.push({});
        if(ejsOptions.drivers.length < 3)ejsOptions.drivers.push({});
        //end tmp
        
        //console.log(ejsOptions.drivers);

        if(fullProfile.vehiclesTrailers){
          ejsOptions.vehiclesTrailers = fullProfile.vehiclesTrailers;

          if(Array.isArray(fullProfile.vehiclesTrailers)){
            for(let c = 0; c < fullProfile.vehiclesTrailers.length; c++){
                if(fullProfile.vehiclesTrailers[c].radiusOfTravel && fullProfile.vehiclesTrailers[c].radiusOfTravel > ejsOptions.radiusOfTravel){
                  ejsOptions.radiusOfTravel = fullProfile.vehiclesTrailers[c].radiusOfTravel;
                }
            }
          }
          
        }
       // console.log('ejsOpttions:'+ JSON.parse(ejsOptions));
        console.log('ejsOpttions2:'+ JSON.stringify(ejsOptions));
        html = ejs.render(contents, ejsOptions);

        resolve(html);


    })
  },
};