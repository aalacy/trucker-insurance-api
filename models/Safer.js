let mongoose = require('mongoose')
require('mongoose-long')(mongoose)

let saferSchema = mongoose.Schema({
    Report_number: {
        type: String,
        required: true
    },
    Report_seq_no: {
        type: String,
        required: true
    },
    DOT_Number: {
        type: String,
        required: true
    },
    Report_Date: {
        type: Date,
        required: true
    },
    Report_State: {
        type: String,
        required: false
    },
    Fatalities: {
        type: Number,
        required: false
    },
    Injuries: {
        type: Number,
        required: false
    },
    Tow_Away: {
        type: String,
        required: false
    },
    Hazmat_released: {
        type: String,
        required: true
    },
    Trafficway_Desc: {
        type: String,
        required: true
    },
    Access_Control_Desc: {
        type: String,
        required: true
    },
    Road_surface_Condition_Desc: {
        type: String,
        required: true
    },
    Weather_Condition_Desc: {
        type: String,
        required: true
    },
    Light_Condition_Desc: {
        type: String,
        required: true
    },
    Vehicle_ID_Number: {
        type: String,
        required: true
    },
    Vehicle_License_number: {
        type: String,
        required: true
    },
    Vehicle_license_state: {
        type: String,
        required: true
    },
    Severity_Weight: {
        type: String,
        required: true
    },
    Time_weight: {
        type: String,
        required: true
    },
    citation_issue_desc: {
        type: String,
        required: true
    },
    seq_num: {
        type: String,
        required: true
    },
    createdAt: { type: Date, default: Date.now }
}, {
    timestamps: true
})

module.exports = mongoose.model('Safer', saferSchema)
