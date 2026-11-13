plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.piflab.partygame"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.piflab.partygame"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Signed with the debug key so the release APK installs directly via Downloader.
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")

    // Local HTTP server: phones on the same Wi-Fi act as game controllers
    implementation("org.nanohttpd:nanohttpd:2.3.1")

    // QR code shown on the TV so players can join by scanning
    implementation("com.google.zxing:core:3.5.3")
}
