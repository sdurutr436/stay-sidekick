import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideIcons } from '@ng-icons/core';
import {
  phosphorBuildings,
  phosphorAddressBook,
  phosphorBellRinging,
  phosphorFireSimple,
  phosphorChatText,
  phosphorUserCircle,
  phosphorGoogleLogo,
  phosphorDatabase,
  phosphorSparkle,
  phosphorSwatches,
  phosphorArrowsClockwise,
  phosphorFileArrowUp,
  phosphorPlus,
  phosphorTrash,
  phosphorInfo,
  phosphorCheckCircle,
  phosphorWarningCircle,
  phosphorUserPlus,
  phosphorCalendar,
  phosphorCalendarCheck,
  phosphorDownloadSimple,
  phosphorPencilSimple,
  phosphorFileText,
  phosphorX,
  phosphorCopy,
  phosphorFloppyDisk,
} from '@ng-icons/phosphor-icons/regular';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withFetch(), withInterceptors([authInterceptor])),
    provideIcons({
      phosphorBuildings,
      phosphorAddressBook,
      phosphorBellRinging,
      phosphorFireSimple,
      phosphorChatText,
      phosphorUserCircle,
      phosphorGoogleLogo,
      phosphorDatabase,
      phosphorSparkle,
      phosphorSwatches,
      phosphorArrowsClockwise,
      phosphorFileArrowUp,
      phosphorPlus,
      phosphorTrash,
      phosphorInfo,
      phosphorCheckCircle,
      phosphorWarningCircle,
      phosphorUserPlus,
      phosphorCalendar,
      phosphorCalendarCheck,
      phosphorDownloadSimple,
      phosphorPencilSimple,
      phosphorFileText,
      phosphorX,
      phosphorCopy,
      phosphorFloppyDisk,
    }),
  ]
};
