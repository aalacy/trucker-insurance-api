let mongoose = require('mongoose')
require('mongoose-long')(mongoose)

let documentSchema = mongoose.Schema({
    imageIdFront: {
        type: Object,
        required: true
    },
    imageIdBack: {
        type: Object,
        required: true
    },
    imageDOT: {
        type: Object,
        required: true
    },
    dataDOT: {
        type: Object,
        required: false
    },
    checkrCandidate: {
        type: Object,
        required: false
    },
    checkrCandidateResponse: {
        type: Object,
        required: false
    },
    resultDOT: {
        type: String,
        required: false
    },
    resultDOTSaferData: {
        type: Object,
        required: false
    },
    imageRegistration: {
        type: Object,
        required: true
    },
    phone: {
        type: String,
        required: true
    },
    email: {
        type: String,
        required: true
    },
    garagingZip: {
        type: Number,
        required: true
    },
    cargoType: {
        type: String,
        required: true
    },
    ownerFirstName: {
        type: String,
        required: true
    },
    ownerLastName: {
        type: String,
        required: true
    },
    ownerStreet: {
        type: String,
        required: true
    },
    ownerCity: {
        type: String,
        required: true
    },
    ownerState: {
        type: String,
        required: true
    },
    ownerZip: {
        type: Number,
        required: true
    },
    ownerCountry: {
        type: String,
        required: true
    },
    ownerDOB: {
        type: String,
        required: true
    },
    yearBusinessStarted: {
        type: String,
        required: true
    },
    electronicDeviceProvider: {
        type: String,
        required: true
    },
    currentInsuranceProvider: {
        type: String,
        required: true
    },
    createdAt: { type: Date, default: Date.now }
}, {
    timestamps: true
})

module.exports = mongoose.model('Document', documentSchema)
