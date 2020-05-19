'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Companies', 'broker_id');
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Companies', 'broker_id', {
        type : Sequelize.INTEGER,
        allowNull : true,
      });
  }
};
