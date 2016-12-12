from louie import dispatcher

from unittest import TestCase
# from twisted.trial import unittest

from pysmhs.fsm.kiosk_fsm import KioskFSM

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

PRODUCT_1 = '1'
PRODUCT_2 = '2'
INVALID_PRODUCT = 'invalid_product'

PRODUCTS = {
            PRODUCT_1 : 10,
            PRODUCT_2 : 100
            }


class TestKioskFsm(TestCase):
    def setUp(self):
        self.fsm_listener = MagicMock()
        self.fsm_listener.ready = MagicMock(spec="ready")
        self.fsm_listener.reset_sell = MagicMock(spec="reset_sell")
        self.fsm_listener.error = MagicMock(spec="error")

        self.cash_fsm = MagicMock()
        self.cash_fsm.start = MagicMock()
        self.cash_fsm.accept = MagicMock()
        self.cash_fsm.dispense_all = MagicMock()
        self.cash_fsm.dispense_change = MagicMock()

        self.plc = MagicMock()
        self.plc.prepare = MagicMock()

        self.kiosk_fsm = KioskFSM(cash_fsm=self.cash_fsm, plc=self.plc,
                                  products=PRODUCTS)

        dispatcher.connect(self.fsm_listener.ready,
                           sender=self.kiosk_fsm, signal='ready')
        dispatcher.connect(self.fsm_listener.reset_sell,
                           sender=self.kiosk_fsm, signal='reset_sell')
        dispatcher.connect(self.fsm_listener.error,
                           sender=self.kiosk_fsm, signal='error')

    def tearDown(self):
        pass

    #                             1    2    3    4    5    6    7    8    9   10   11
    # inputs
    # fsm.state("INI",           INI  INI  INI  INI  INI  INI  INI  INI  INI  INI  INI
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                            +
    # cash_fsm.ready                        +
    # cash_fsm.error                             +
    # cash_fsm.not_accepted                           +
    # cash_fsm.accepted                                    +
    # cash_fsm.dispensed                                        +
    # plc.prepared                                                   +
    # plc.not_prepared                                                    +
    # sell (valid product)                                                     +
    # sell (invalid product)                                                        +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    -    -    -    -    -    -    -    -    -
    # cash_fsm.start              -    +    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    -    -    -    -    -    -    -    -    -

    def test_1_init(self):
        self.check_outputs()

    def test_2_kiosk_start_on_init(self):
        self.kiosk_fsm.start()

        self.check_outputs(cash_fsm_start_expected=[()])

    def test_3_cash_ready_on_init(self):
        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs()

    def test_4_cash_error_on_init(self):
        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs()

    def test_5_not_accepted_on_init(self):
        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs()

    def test_6_accepted_on_init(self):
        self.kiosk_fsm.amount_accepted()

        self.check_outputs()

    def test_7_dispensed_on_init(self):
        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_8_prepared_on_init(self):
        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_9_not_prepared_on_init(self):
        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_10_sell_valid_product_on_init(self):
        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_11_sell_invalid_product_on_init(self):
        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    #                            12   13   14   15   16   17   18   19   20   21
    # inputs
    # fsm.state("INI",           WR   WR   WR   WR   WR   WR   WR   WR   WR   WR
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    #
    # outputs
    # fsm_listener.ready          -    +    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    +    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    +    -    -    -    -    -    -    -

    def test_12_kiosk_start_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.start()

        self.check_outputs()

    def test_13_cash_ready_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs(fsm_ready_expected=[()])

    def test_14_cash_error_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code': 12,
                                  'error_text': 'error_12'},)],
            kiosk_fsm_error=True)

    def test_15_not_accepted_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs()

    def test_16_accepted_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.amount_accepted()

        self.check_outputs()

    def test_17_dispensed_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_18_prepared_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_19_not_prepared_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_20_sell_valid_product_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_21_sell_invalid_product_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    #                            22   23   24   25   26   27   28   29   30   31
    # inputs
    # fsm.state("INI",           ERR  ERR  ERR  ERR  ERR  ERR  ERR  ERR  ERR  ERR
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    -    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    -    -    -    -    -    -    -    -

    def test_22_kiosk_start_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.start()

        self.check_outputs()

    def test_23_cash_ready_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs()

    def test_24_cash_error_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs()

    def test_25_not_accepted_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs()

    def test_26_accepted_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.amount_accepted()

        self.check_outputs()

    def test_27_dispensed_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_28_prepared_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_29_not_prepared_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_30_sell_valid_product_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_31_sell_invalid_product_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    #                            32   33   34   35   36   37   38   39   40   41
    # inputs
    # fsm.state("INI",           RDY  RDY  RDY  RDY  RDY  RDY  RDY  RDY  RDY  RDY
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -    -    +
    # fsm_listener.error          -    -    +    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    +    -
    # cash_fsm.dispense_all       -    -    +    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    +    -    -    -    -    -    -    -

    def test_32_kiosk_start_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.start()

        self.check_outputs()

    def test_33_cash_ready_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs()

    def test_34_cash_error_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            cash_fsm_dispense_all_expected=[()],
            kiosk_fsm_error=True)

    def test_35_not_accepted_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs()

    def test_36_accepted_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.amount_accepted()

        self.check_outputs()

    def test_37_dispensed_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_38_prepared_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_39_not_prepared_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_40_sell_valid_product_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs(
               cash_fsm_accept_expected=[((PRODUCTS[PRODUCT_1],),)])

    def test_41_sell_invalid_product_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs(fsm_reset_sell_expected=[()],
                           fsm_ready_expected=[()])

    #                            42   43   44   45   46   47   48   49   50   51
    # inputs
    # fsm.state("INI",           SS   SS   SS   SS   SS   SS   SS   SS   SS   SS
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    +    -    -    -    -    -    -
    # fsm_listener.error          -    -    -    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    +    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    +    -    -    -    -    -    -    -

    def test_42_kiosk_start_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.start()

        self.check_outputs()

    def test_43_cash_ready_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs()

    def test_44_cash_error_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs(kiosk_fsm_error=True)

    def test_45_not_accepted_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs(fsm_reset_sell_expected=[()],
                           fsm_ready_expected=[()])

    def test_46_accepted_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.amount_accepted()

        self.check_outputs(plc_prepare_expected=[((PRODUCT_1,),)])

    def test_47_dispensed_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_48_prepared_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_49_not_prepared_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_50_sell_valid_product_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_51_sell_invalid_product_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    #                            52   53   54   55   56   57   58   59   60   61
    # inputs
    # fsm.state("INI",           SP   SP   SP   SP   SP   SP   SP   SP   SP   SP
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    -    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    +    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    +    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    +    -    -    -    -    -    -    -

    def test_52_kiosk_start_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.start()

        self.check_outputs()

    def test_53_cash_ready_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs()

    def test_54_cash_error_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs(kiosk_fsm_error=True)

    def test_55_not_accepted_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs()

    def test_56_accepted_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.amount_accepted()

        self.check_outputs()

    def test_57_dispensed_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_58_prepared_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.prepared()

        self.check_outputs(cash_fsm_dispense_change_expected=[()])

    def test_59_not_prepared_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.not_prepared()

        self.check_outputs(cash_fsm_dispense_all_expected=[()])

    def test_60_sell_valid_product_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_61_sell_invalid_product_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    #                            62   63   64   65   66   67   68   69   70   71
    # inputs
    # fsm.state("INI",           SD   SD   SD   SD   SD   SD   SD   SD   SD   SD
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    +    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    -    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    +    -    -    -    -    -    -    -

    def test_62_kiosk_start_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.start()

        self.check_outputs()

    def test_63_cash_ready_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.cash_fsm_ready()

        self.check_outputs()

    def test_64_cash_error_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs(kiosk_fsm_error=True)

    def test_65_not_accepted_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs()

    def test_66_accepted_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.amount_accepted()

        self.check_outputs()

    def test_67_dispensed_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs(fsm_ready_expected=[()])

    def test_68_prepared_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_69_not_prepared_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_70_sell_valid_product_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_71_sell_invalid_product_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    #                            72   73   74   75   76   77   78
    # inputs
    # fsm.state("INI",           INI  WR   ERR  RDY  SS   SP   SD
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD")
    # cash_fsm.fatal              +    +    +    +    +    +    +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -
    # fsm_listener.error          -    +    -    +    +    -    +
    # cash_fsm.start              -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    +    +    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    +    -    +    +    +    +

    def test_72_fatal_on_init(self):
        self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')

        self.check_outputs()

    def test_73_fatal_on_wait_ready(self):
        self.set_fsm_state_wait_ready()

        self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            kiosk_fsm_error=True)

    def test_74_fatal_on_error(self):
        self.set_fsm_state_error()

        self.kiosk_fsm.cash_fsm_fatal(error_code=15, error_text='error_15')

        self.check_outputs()

    def test_75_fatal_on_ready(self):
        self.set_fsm_state_ready()

        self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            cash_fsm_dispense_all_expected=[()],
            kiosk_fsm_error=True)

    def test_76_fatal_on_start_sell(self):
        self.set_fsm_state_start_sell(product=PRODUCT_1)

        self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            cash_fsm_dispense_all_expected=[()],
            kiosk_fsm_error=True)

    def test_77_fatal_on_start_prepare(self):
        self.set_fsm_state_start_prepare()

        self.check_outputs()

    def test_78_fatal_on_start_dispense(self):
        self.set_fsm_state_start_dispense()

        self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            kiosk_fsm_error=True)

    #                            79   80   81   82   83   84   85   86   87   88   89
    # inputs
    # fsm.state("INI",           AA   AA   AA   AA   AA   AA   AA   AA   AA   AA   AA
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD",
    #          "AA")
    # start                       +
    # cash_fsm.ready                   +
    # cash_fsm.error                        +
    # cash_fsm.not_accepted                      +
    # cash_fsm.accepted                               +
    # cash_fsm.dispensed                                   +
    # plc.prepared                                              +
    # plc.not_prepared                                               +
    # sell (valid product)                                                +
    # sell (invalid product)                                                   +
    # cash_fsm.fatal                                                                +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    +    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    +    -    -    -    -    -    -    -    +
    # cash_fsm.start              -    -    -    -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_all       -    -    +    -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    +    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    +    -    -    -    -    -    -    -    +

    def test_79_start_on_accept_amount(self):
        self.set_fsm_state_accept_amount()
        self.kiosk_fsm.start()
        self.check_outputs()

    def test_80_cash_ready_on_accept_amount(self):
        self.set_fsm_state_accept_amount()
        self.kiosk_fsm.cash_fsm_ready()
        self.check_outputs()

    def test_81_cash_error_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.cash_fsm_error(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            cash_fsm_dispense_all_expected=[()],
            kiosk_fsm_error=True)

    def test_82_not_accepted_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.amount_not_accepted()

        self.check_outputs(fsm_reset_sell_expected=[()],
                           fsm_ready_expected=[()])

    def test_83_accepted_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.amount_accepted()

        self.check_outputs(cash_fsm_dispense_change_expected=[()])

    def test_84_dispensed_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.amount_dispensed()

        self.check_outputs()

    def test_85_prepared_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.prepared()

        self.check_outputs()

    def test_86_not_prepared_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.not_prepared()

        self.check_outputs()

    def test_87_sell_valid_product_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.sell(product=PRODUCT_1)

        self.check_outputs()

    def test_88_sell_invalid_product_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.sell(product=INVALID_PRODUCT)

        self.check_outputs()

    def test_89_fatal_on_accept_amount(self):
        self.set_fsm_state_accept_amount()

        self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')

        self.check_outputs(
            fsm_error_expected=[({'error_code':12,
                                  'error_text':'error_12'},)],
            kiosk_fsm_error=True)

    #                            90   91   92   93   94   95   96   97
    # inputs
    # fsm.state("INI",           INI  WR   ERR  RDY  SS   SP   SD   AA
    #          "WR",
    #          "ERR",
    #          "RDY",
    #          "SS",
    #          "SP",
    #          "SD",
    #          "AA")
    # accept_amount               +    +    +    +    +    +    +    +
    #
    # outputs
    # fsm_listener.ready          -    -    -    -    -    -    -    -
    # fsm_listener.reset_sell     -    -    -    -    -    -    -    -
    # fsm_listener.error          -    -    -    -    -    -    -    -
    # cash_fsm.start              -    -    -    -    -    -    -    -
    # cash_fsm.accept             -    -    -    +    -    -    -    -
    # cash_fsm.dispense_all       -    -    -    -    -    -    -    -
    # cash_fsm.dispense_change    -    -    -    -    -    -    -    -
    # plc.prepare                 -    -    -    -    -    -    -    -
    # kiosk_fsm.has_error         -    -    -    -    -    -    -    -

    # def test_72_fatal_on_init(self):
    #     self.kiosk_fsm.cash_fsm_fatal(error_code=12, error_text='error_12')
    #
    #     self.check_outputs()

    def set_fsm_state_wait_ready(self):
        self.kiosk_fsm.start()
        self.cash_fsm.start.reset_mock()

    def set_fsm_state_ready(self):
        self.set_fsm_state_wait_ready()
        self.kiosk_fsm.cash_fsm_ready()
        self.fsm_listener.ready.reset_mock()

    def set_fsm_state_error(self):
        self.set_fsm_state_ready()
        self.kiosk_fsm.cash_fsm_error(error_code='12', error_text='error_12')
        self.fsm_listener.error.reset_mock()
        self.cash_fsm.dispense_all.reset_mock()
        self.kiosk_fsm._has_error = False

    def set_fsm_state_start_sell(self, product=PRODUCT_1):
        self.set_fsm_state_ready()
        self.kiosk_fsm.sell(product=product)
        self.cash_fsm.accept.reset_mock()

    def set_fsm_state_start_prepare(self,
                                    product=PRODUCT_1,
                                    amount=PRODUCTS[PRODUCT_1]):
        self.set_fsm_state_start_sell(product=product)
        self.kiosk_fsm.amount_accepted(amount=amount)
        self.plc.prepare.reset_mock()

    def set_fsm_state_start_dispense(self,
                                     product=PRODUCT_1,
                                     amount=PRODUCTS[PRODUCT_1]):
        self.set_fsm_state_start_prepare(product=product, amount=amount)
        self.kiosk_fsm.prepared()
        self.cash_fsm.dispense_change.reset_mock()

    def set_fsm_state_accept_amount(self,
                                     amount=PRODUCTS[PRODUCT_1]):
        self.set_fsm_state_ready()
        self.kiosk_fsm.accept_amount(amount)
        self.cash_fsm.accept.reset_mock()

    def check_outputs(self,
                      fsm_ready_expected=[],
                      fsm_reset_sell_expected=[],
                      fsm_error_expected=[],
                      cash_fsm_start_expected=[],
                      cash_fsm_accept_expected=[],
                      cash_fsm_dispense_all_expected=[],
                      cash_fsm_dispense_change_expected=[],
                      plc_prepare_expected=[],
                      kiosk_fsm_error=False):
        self.assertEquals(fsm_ready_expected,
                          self.fsm_listener.ready.call_args_list)
        self.assertEquals(fsm_reset_sell_expected,
                          self.fsm_listener.reset_sell.call_args_list)
        self.assertEquals(fsm_error_expected,
                          self.fsm_listener.error.call_args_list)
        self.assertEquals(cash_fsm_start_expected,
                          self.cash_fsm.start.call_args_list)
        self.assertEquals(cash_fsm_accept_expected,
                          self.cash_fsm.accept.call_args_list)
        self.assertEquals(cash_fsm_dispense_all_expected,
                          self.cash_fsm.dispense_all.call_args_list)
        self.assertEquals(cash_fsm_dispense_change_expected,
                          self.cash_fsm.dispense_change.call_args_list)
        self.assertEquals(plc_prepare_expected,
                          self.plc.prepare.call_args_list)
        self.check_kiosk_fsm_error(kiosk_fsm_error)

    def check_kiosk_fsm_error(self, kiosk_fsm_error=False):
        self.assertEquals(kiosk_fsm_error,
                          self.kiosk_fsm.has_error())
