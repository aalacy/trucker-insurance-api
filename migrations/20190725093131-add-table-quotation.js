'use strict';

module.exports = {
  up: (queryInterface, Sequelize) => {
    return queryInterface.createTable('Quotation', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      broker_id: {
        type: Sequelize.INTEGER,
        allowNull:false
      },
      uuid:{
        type: Sequelize.STRING,
        allowNull:false
      },
      user_id:{
        type:Sequelize.INTEGER,
        allowNull:false
      },
      auto_liability:{
        type: Sequelize.TINYINT(1),
        allowNull:true
      },
      bpid:{
        type:Sequelize.STRING,
        allowNull:true
      },
      umbi:{
        type:Sequelize.STRING,
        allowNull:true
      },
      umpd:{
        type: Sequelize.STRING,
        allowNull:false
      },
      med_pay:{
        type:Sequelize.STRING,
        allowNull:true
      },
      rental_reimbursement:{
        type:Sequelize.STRING,
        allowNull:true
      },
      down_time_rental:{
        type:Sequelize.STRING,
        allowNull:true
      },
      physical_damage:{
        type: Sequelize.STRING,
        allowNull:false
      },
      comprehensive_ded:{
        type: Sequelize.STRING,
        allowNull:false 
      },
      collision_ded:{
        type:Sequelize.STRING,
        allowNull:true
      },
      value_of_vehicle_traile:{
        type:Sequelize.STRING,
        allowNull:true
      },cargo:{
        type:Sequelize.STRING,
        allowNull:true
      },
      cargo_limits:{
        type:Sequelize.STRING,
        allowNull:true
      },cargo_deductible:{
        type:Sequelize.STRING,
        allowNull:true
      },umbrella_or_excess_liability:{
        type:Sequelize.STRING,
        allowNull:true
      }, each_occurrence:{
        type:Sequelize.STRING,
        allowNull:true
      },aggregate:{
        type:Sequelize.STRING,
        allowNull:true
      },deductible_or_retention:{
        type:Sequelize.STRING,
        allowNull:true
      },general_liability:{
        type:Sequelize.STRING,
        allowNull:true
      },each_occurrence:{
        type:Sequelize.STRING,
        allowNull:true
      },damage_to_rented_premises:{
        type:Sequelize.STRING,
        allowNull:true
      },med_exp:{
        type:Sequelize.STRING,
        allowNull:true
      },personal_adv_injury:{
        type:Sequelize.STRING,
        allowNull:true
      },general_aggregate:{
        type:Sequelize.STRING,
        allowNull:true
      },
      products_and_completed_operations:{
        type:Sequelize.STRING,
        allowNull:true
      },workers_compensation:{
        type:Sequelize.STRING,
        allowNull:true
      },each_accident:{
        type:Sequelize.STRING,
        allowNull:true
      },disease_each_employees :{
        type:Sequelize.STRING,
        allowNull:true
      },disease_policy_limits:{
        type:Sequelize.STRING,
        allowNull:true
      },trailer_interchange:{
        type:Sequelize.STRING,
        allowNull:true
      },trailer_interchange_limits:{
        type:Sequelize.STRING,
        allowNull:true
      },trailer_interchange_deductible:{
        type:Sequelize.STRING,
        allowNull:true
      },refer_breakdown:{
        type:Sequelize.STRING,
        allowNull:true
      },claims_made:{
        type:Sequelize.STRING,
        allowNull:true
      },per_occurrence:{
        type:Sequelize.STRING,
        allowNull:true
      },any_auto:{
        type:Sequelize.STRING,
        allowNull:true
      },hired_auto:{
        type:Sequelize.STRING,
        allowNull:true
      },employer_non_owned_auto:{
        type:Sequelize.STRING,
        allowNull:true
      },scheduled_auto:{
        type:Sequelize.STRING,
        allowNull:true
      },all_owned_autos:{
        type:Sequelize.STRING,
        allowNull:true
      },client_approval:{
        type: Sequelize.TINYINT(1),
        allowNull:true
      },ready_to_client:{
        type: Sequelize.TINYINT(1),
        allowNull:true
      },
      request_re_quote:{
        type: Sequelize.TINYINT(1),
        allowNull:true
      }

    }
    )},

  down: (queryInterface, Sequelize) => {
    return queryInterface.dropTable('Quotation');
    /*
      Add reverting commands here.
      Return a promise to correctly handle asynchronicity.

      Example:
      return queryInterface.dropTable('users');
    */
  }
};
