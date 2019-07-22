let states = require('./states')
module.exports = {
    extractDOT: (data) => {
        let rows = data.description.split("\n")
        let ret = false
        rows.forEach(row => {
            if (row.search('DOT') >= 0) {
                ret = row
                return
            }
        })
        return ret
    },
    extractDLId: data => {
        let rows = data.description.split("\n")
        console.log(rows)
        let rowArr = rows[2].split(" ")
        return rowArr[rowArr.length - 1]
    },
    extractDLState: data => {
        let rows = data.description.split(" ")
        let ret = false
        states.list.forEach(state => {
            if (state.name.toLowerCase() == rows[0].toLowerCase()) {
                ret = state.abbreviation
                return
            }
        })
        return ret
    }
}
