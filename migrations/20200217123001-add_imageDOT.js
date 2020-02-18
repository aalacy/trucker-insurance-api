'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn(
      'Companies',
      'imageDOT',
     Sequelize.JSON
    );
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn(
      'Companies',
      'imageDOT'
    );
  }
};
