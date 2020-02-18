'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn(
      'Companies',
      'imageIdBack',
     Sequelize.JSON
    );
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn(
      'Companies',
      'imageIdBack'
    );
  }
};
