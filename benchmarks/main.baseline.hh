#ifndef MAIN_HH
#define MAIN_HH 


// matrix vector multiplication 128 * 1024
#define MVS_S2__PER_LINE     20
#define MVS_S2__BANDWIDTH    50
#define MVS_S2__REPETITIONS  1000*16*16

// matrix vector multiplication 1024 * 8192
#define MVS_S3__PER_LINE     50
#define MVS_S3__BANDWIDTH    50
#define MVS_S3__REPETITIONS  1000*10

// matrix matrix multiplication 32 * 32
#define MMS_S2__PER_LINE     4
#define MMS_S2__BANDWIDTH    8
#define MMS_S2__REPETITIONS  100*16

// matrix matrix multiplication 128 * 128
#define MMS_S3__PER_LINE     10
#define MMS_S3__BANDWIDTH    20
#define MMS_S3__REPETITIONS  16


#endif // MAIN_HH
