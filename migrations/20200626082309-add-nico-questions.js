'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.addColumn('Companies', 'nico_questions', {
      type : Sequelize.JSON,
      allowNull : true,
    });
  },

  down: (queryInterface, Sequelize) => {
    return queryInterface.removeColumn('Companies', 'nico_questions');
  }
};
