'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn(
      'Companies',
      'imageIdFront',
     Sequelize.JSON
    );
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn(
      'Companies',
      'imageIdFront'
    );
  }
};
