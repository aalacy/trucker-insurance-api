'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Companies', 'user_id');
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Companies', 'user_id', {
        type : Sequelize.INTEGER,
        allowNull : true,
      });
  }
};
