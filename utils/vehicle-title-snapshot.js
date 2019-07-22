const vision = require('@google-cloud/vision')
const cheerio = require('cheerio');
const client = new vision.ImageAnnotatorClient()
const vin = require('vin-lite');
const LookupVehicle = require('lookup_vehicle');
const fs = require('fs');
const request = require("request");
const tabletojson = require('tabletojson');

module.exports = {
  
  states: ['alabama','alaska','american samoa','arizona','arkansas','california','colorado','connecticut','delaware','district of columbia','federated states of micronesia','florida','georgia','guam','hawaii','idaho','illinois','indiana','iowa','kansas','kentucky','louisiana','maine','marshall islands','maryland','massachusetts','michigan','minnesota','mississippi','missouri','montana','nebraska','nevada','new hampshire','new jersey','new mexico','new york','north carolina','north dakota','northern mariana islands','ohio','oklahoma','oregon','palau','pennsylvania','puerto rico','rhode island','south carolina','south dakota','tennessee','texas','utah','vermont','virgin island','virginia','washington','west virginia','wisconsin','wyoming'],
  scan: async function(location) {
    return new Promise(async (resolve, reject) => {

      let result = {};
      let _this = this;

      let ret;
      try{
          ret = await client.textDetection(location);
        }catch(e){
          reject(e);
          return
        }

      if(!ret || ret.length === 0){
        reject('not found');
        return;
      }
      let labels = ret[0];
      
      try{
        
        for(let index = 0; labels.textAnnotations[index]; index++){
            let item = labels.textAnnotations[index];

            if(_this.states.indexOf(item.description.toLowerCase()) > -1){
              result.state = item.description;
              continue;
            }

            if(!result.vin){

              let vin_candidate = item.description.trim().replace('O', '0');
              for(let c = index+1; vin_candidate.length < 17 && labels.textAnnotations[c]; c++){
                vin_candidate += labels.textAnnotations[c].description.trim();
              }
              //console.log('~~~',vin_candidate,'|'+(vin_candidate.length)+'|'+vin_candidate[8]+'~~~');
              
              if(vin_candidate.length === 17 && (vin_candidate[8] === 'X' || vin_candidate[8].match(/[0-9]/i))){
                
                let _vdata;
                //console.log('*****',vin_candidate,'*****');
                
                try{
                  _vdata = await LookupVehicle.lookup(vin_candidate);
                }catch(e){
                   reject(e);
                }

                //console.log(_vdata.data.Results);
                if(_vdata.data.Results && (_vdata.data.Results[0].Model || _vdata.data.Results[0].Make)){
                    result.VINDetails = _vdata.data.Results[0]
                    result.vin = vin_candidate;
                    break;
                }
              }
            }

            //console.log("#"+index+" - "+item.description+";\r\n");
        }

        if(result.vin){
          result.vehicleHistory = await this.getVehicleHistory(result.vin);
          resolve(result);
        }else{
          reject({error: 'vin is empty or wrong'});
        }
      }catch(e){
        reject(e);
      }

      

    })
  },
  test: function() {
    let html = fs.readFileSync('test4.html', 'utf8');
    return this.parseHTML(html);
  },
  getVehicleHistory: async function(vin) {
    return new Promise((resolve, reject) => {

      let _this = this;
      request(
          { headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
          },
          uri: "https://www.vehiclehistory.com/vin-report/"+vin },
          function(error, response, body) {
              if(error){
                reject("Got error: " + error);
                return;
              }
              if(!body){
                reject("empty response from the server");
                return;
              }

              //console.log(body);

              resolve(_this.parseHTML(body));
          }
      );

    })
  },
  parseHTML: function(html) {
    const $ = cheerio.load(html);
    let ret = {};

    $("div[data-cy=vin-junk-salvage-insurances-records]").map(function (i, element){
      
        ret['junkSalvageInsurance'] = [];
        $(element).find('.Card').map(function (i1, element1){
          
          let tmp = {};
          
          /******** Junk/Salvage/Insurance ********/ 

          let lines = $(element1).find("div[class='Card-contentContainer']").text().split('\n').map(function(item) {
            return item.trim();
          }).filter(function(el) { return el; });

          lines.map(function (element, i){
             //console.log(element);
             if(i === 0)tmp['name'] = element;
             else if(i === 1)tmp['location'] = element;
             else if(element.includes("Phone"))tmp['phone'] = element.replace('Phone:', '').trim();
             else if(element.includes("Email"))tmp['email'] = element.replace('Email:', '').trim();
             else if(element.includes("Damage Type"))tmp['damageType'] = element.replace('Damage Type:', '').trim();
             else if(element.includes("Disposition"))tmp['disposition'] = element.replace('Disposition:', '').trim();
             else{
               if(!tmp['other'])tmp['other'] = [];
               tmp['other'].push(element);
             }
          });
          tmp['date'] = $(element1).find("div[class='Card-header Card-header--danger'] > span").text().trim();

          ret['junkSalvageInsurance'].push(tmp);
        
          /******** END ********/ 

        }).get()

    }).get()


    /******** Detailed Vehicle History ********/

    $("table[class='VinReport-table u-sm-hidden']").map(function (i, element){
      ret['detailedVehicleHistory'] = tabletojson.convert(cheerio.html(element), { useFirstRowForHeadings: true })[0];
    }).get()

    /******** END ********/ 

    return ret;
  },
  
};