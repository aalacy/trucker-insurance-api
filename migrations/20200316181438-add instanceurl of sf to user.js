'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Users', 'sf_instance_url', {
        type : Sequelize.STRING,
        allowNull : false,
        defaultValue: '',
      });
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Users', 'sf_instance_url');
  }
};
