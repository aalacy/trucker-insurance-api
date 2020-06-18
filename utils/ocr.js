const vision = require('@google-cloud/vision');
const client = new vision.ImageAnnotatorClient();
const { parse } = require('parse-usdl')

module.exports = {
 	dot: async function(location) {
 		return new Promise(async (resolve, reject) => {
  			// Performs DOT number detection on the image file
  			try {
				const [result] = await client.textDetection(location);
				if (result) {
					const fullText = result.fullTextAnnotation;
					console.log('full text:', fullText.text);

					// parse dot
					const blocks = fullText.text.split('\n')
					let value = -1
					blocks.forEach(block => {
						if (block.toLowerCase().includes('dot')) {
							value = block.replace(/\D/g, "");
						}
					})
					
					if (value > 0) {
						resolve({ status: 'success', value, message: 'Successfully read the dot number.'})
					} else {
						reject({ status: 'danger', message:'Sorry, A dot number not found. Please try with different image.'})
					}
				}
			} catch (e) {
				console.log(e)
				reject({ status: 'danger', message:'Sorry, A dot number not found. Please try with different image.'})
			}
		})
	},

	vin: async function(location) {
		return new Promise(async (resolve, reject) => {
			// Performs Driver License detection on the image file
  			try {
				const [result] = await client.textDetection(location);
				if (result) {
					const fullText = result.fullTextAnnotation;
					console.log('full text:', fullText.text);

					// parse VIN
					const blocks = fullText.text.split('\n')
					let value = ''
					blocks.forEach(block => {
						const regex = /VIN ([a-zA-Z0-9_-]){17,19}$/;
						const found = block.trim().match(regex);
						if (found) {
							value = block.split(' ')[1].trim()
						}
					})
					
					console.log(value)
					if (value > 0) {
						resolve({ status: 'success', value, message: 'Successfully read the VIN number'})
					} else {
						reject({ status: 'danger', message:'Sorry, A VIN not found. Please try with different image.'})
					}
				}
			} catch (e) {
				console.log(e)
				reject({ status: 'danger', message:'Sorry, A VIN not found. Please try with different image.'})
			}
		})
	},

	dl: async function(resultCode) {
		return new Promise(async (resolve, reject) => {
			// Performs Driver License detection on the image file
  			try {
				const value = parse(resultCode, {
				    suppressErrors: true
				})
				if (value) {
					value.address = value.addressStreet
					value.city = value.addressCity
					value.state = value.addressState
					value.zip = value.addressPostalCode
					value.licenseNumber = value.documentNumber
					if (value.dateOfBirth) {
						const dob = value.dateOfBirth.split('-')
						value.dobM = dob[1]
						value.dobD = dob[2]
						value.dobY = dob[0]
					}
					resolve({ status: 'success', value: JSON.stringify(value), message: 'Successfully read the DL'})
				} else {
					reject({ status: 'danger', message:'Sorry, A DL not found. Please try with different image.'})
				}
		  	} catch (err) {
			    console.log(err)
				reject({ status: 'danger', message:'Sorry, A DL not found. Please try with different image.'})
		  	}
		})
	}
};