const vision = require('@google-cloud/vision')
const client = new vision.ImageAnnotatorClient()
const fs = require('fs');
const request = require("request");
const parseAddress = require('parse-address');

module.exports = {
  
  states: ['alabama','alaska','american samoa','arizona','arkansas','california','colorado','connecticut','delaware','district of columbia','federated states of micronesia','florida','georgia','guam','hawaii','idaho','illinois','indiana','iowa','kansas','kentucky','louisiana','maine','marshall islands','maryland','massachusetts','michigan','minnesota','mississippi','missouri','montana','nebraska','nevada','new hampshire','new jersey','new mexico','new york','north carolina','north dakota','northern mariana islands','ohio','oklahoma','oregon','palau','pennsylvania','puerto rico','rhode island','south carolina','south dakota','tennessee','texas','utah','vermont','virgin island','virginia','washington','west virginia','wisconsin','wyoming'],
  scan: async function(location) {
    console.log('peetttttttttt.........');
    return new Promise(async (resolve, reject) => {

      let result = {};
      let _this = this;

      let ret;
      try{
        console.log('peet.........');
          ret = await client.textDetection(location);
          console.log('kkk.........',ret);
        }catch(e){
          console.log('lll.........',e);
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

            //console.log("#"+index+" - "+item.description+"; \r\n");
            
            if(_this.states.indexOf(item.description.toLowerCase()) > -1){
              result.state = item.description;
              continue;
            }

            let cond1 = (item.description.toLowerCase() === 'dl' || item.description.toLowerCase() === 'dln');
            let cond2 = ((item.description.toLowerCase() === 'l' || item.description.toLowerCase() === 'd') && labels.textAnnotations[index+2].description.toLowerCase() == 'exp');

            if(!result.driverLicenseNumber && (cond1 || cond2)){
              index++;
              result.licenseNumber = labels.textAnnotations[index].description;
              continue;
            }

            if(item.description.toLowerCase() === 'fn'){
              index++;
              result.firstName = labels.textAnnotations[index].description;
              index++;

              if (isNaN(parseInt(labels.textAnnotations[index].description[0], 10))) {
                result.firstName += " "+labels.textAnnotations[index].description;
                index++;
              }

              let address = [];
              for(index; labels.textAnnotations[index].description !== 'DOB'; index++){
                address.push(labels.textAnnotations[index].description);
              }

              address_str = address.join(' ');


              if(address_str){
                parsed = parseAddress.parseLocation(address_str);
                let tmp_address = [];
    
                if(parsed.number)tmp_address.push(parsed.number); 
                if(parsed.prefix)tmp_address.push(parsed.prefix); 
                if(parsed.street)tmp_address.push(parsed.street); 
    
                if(tmp_address.length)result.address = tmp_address.join(' ');
                if(parsed.city)result.city = parsed.city;
                if(parsed.zip)result.zip = parsed.zip;
                if(parsed.state/* && !result.state*/)result.state = parsed.state;
              }

              index--;
              continue;
            }

            if(item.description.toLowerCase() === 'class'){
              index++;
              result.class = labels.textAnnotations[index].description;
              continue;
            }

            if(item.description.toLowerCase() === 'ln'){
              index++;
              result.lastName = labels.textAnnotations[index].description;
              continue;
            }

            if(item.description.toLowerCase() === 'dob'){
              index++;
              result.dateOfBirth = labels.textAnnotations[index].description;
              continue;
            }

/*
            if(!result.vin){

              let vin_candidate = item.description.trim();
              for(let c = index+1; vin_candidate.length < 17 && labels.textAnnotations[c]; c++){
                vin_candidate += labels.textAnnotations[c].description.trim();
              }
              //console.log('~~~',vin_candidate,'~~~');
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
            }*/

            
        }


        resolve(result);

      }catch(e){
        reject(e);
      }

      

    })
  },
  test: function() {
    let html = fs.readFileSync('test4.html', 'utf8');
    return this.parseHTML(html);
  },
  
};