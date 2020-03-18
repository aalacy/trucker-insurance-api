'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Users', 'dotId', {
        type : Sequelize.INTEGER,
        allowNull : true,
      });
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Users', 'dotId');
  }
};
