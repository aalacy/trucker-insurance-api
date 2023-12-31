'use strict';

module.exports = {
    up: (queryInterface, Sequelize) => {
     return queryInterface.addColumn('Users', 'admin', {
         type : Sequelize.INTEGER,
         defaultValue : 0,
         allowNull : false
     })
    },

    down: (queryInterface, Sequelize) => {
        return queryInterface.removeColumn('Users', 'admin')
    }
};
