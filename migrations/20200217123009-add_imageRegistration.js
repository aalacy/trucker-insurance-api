'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn(
      'Companies',
      'imageRegistration',
     Sequelize.JSON
    );
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn(
      'Companies',
      'imageRegistration'
    );
  }
};
